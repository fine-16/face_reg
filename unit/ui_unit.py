import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk, ImageOps  # 画像データ用
from picamera2.picamera2 import Picamera2


class AttendanceApp:

    def __init__(self, window, camera_unit, face_recognizer, database):
        self.window = window
        self.window.title("勤怠管理システム")

        #camera_unitとface_recognizerとDBのインスタンスを受け取る

        #get_frame()でPILの状態で画像を取得する
        #close()でカメラを解放する
        self.camera_unit = camera_unit
       
        #recognize_face(pil_image)で顔認識を行う best_personが返ってくる
        self.face_recognizer = face_recognizer
        
        
        #insert_record(name, status)でDBにレコードを挿入する
        #get_last_record()で最後のレコードを取得する
        self.database = database



        #cameraはCameraUnitのクラスを使う
        '''
        # 1. カメラの初期化
        self.picam2 = Picamera2()
        self.picam2.start()
        #カメラの映像を取得するための変数を設定
        self.capture=self.picam2.capture_array()
        '''

        # 全体のレイアウト設定（左右のフレームを作成）
        self.left_frame = tk.Frame(window)
        self.left_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.right_frame = tk.Frame(window)
        self.right_frame.pack(
            side=tk.RIGHT, padx=20, pady=20, fill=tk.Y, expand=True
        )

        # 左フレーム：カメラ映像を表示する空のCanvasを作成
        self.canvas = tk.Canvas(self.left_frame)
       
        # Canvasを配置
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # 右フレーム：名前「入力欄」への変更
        self.name_text = "適切な位置に顔を合わせてください"
        self.name_title_label = tk.Label(
            self.right_frame, text= self.name_text
        )
        self.name_title_label.pack(pady=(20, 5))

        #  右フレーム：出勤・退勤ボタン
        self.btn_attendance = tk.Button(
            self.right_frame,
            text="出勤",
            bg="#2ecc71",
            fg="white",
           
            width=15,
            height=2,
            command=self.on_attendance,
        )
        self.btn_attendance.pack(pady=10)

        self.btn_leaving = tk.Button(
            self.right_frame,
            text="退勤",
            bg="#e74c3c",
            fg="white",
            
            width=15,
            height=2,
            command=self.on_leaving,
        )
        self.btn_leaving.pack(pady=10)

        # 最後に入力された勤怠を表示
        self.last_record = "ここに最終操作が表示されます"
        self.last_record_label = tk.Label(
            self.right_frame, text= self.last_record
        )
        self.last_record_label.pack(pady=(20, 5))

        # 映像更新ループの開始
        self.disp_image()

        #名前の更新ループの開始
        self.disp_best_person_name()

        #データベースからの読み取りループの開始
        self.disp_last_record()


        # ウィンドウが閉じられたときの終了処理を登録
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)


    #顔の推定値はこれに渡す
    def disp_best_person_name(self):

        #推定するカメラ画像の取得
        #pilimageをframeに渡す
        pil_image = self.camera_unit.get_frame() 

        #face_recognizerでカメラ画像が登録されている人のうちの誰に一番近いか推測して表示する
        best_person_name = self.face_recognizer.recognize_face(pil_image)
        self.name_text = best_person_name

        # disp_image()を500msec後に実行する
        self.after(500, self.disp_best_person_name)


    def disp_image(self):
        #画像をCanvasに表示する

        
        # フレーム画像の取得
        #frame = self.capture

        # BGR→RGB変換
        #cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # NumPyのndarrayからPillowのImageへ変換
        #pil_image = Image.fromarray(cv_image)
        

        # キャンバスのサイズを取得
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        #pilimageをframeに渡す
        pil_image = self.camera_unit.get_frame() 

        # 画像のアスペクト比（縦横比）を崩さずに指定したサイズ（キャンバスのサイズ）全体に画像をリサイズする
        pil_image = ImageOps.pad(pil_image, (canvas_width, canvas_height))

        # PIL.ImageからPhotoImageへ変換する
        self.photo_image = ImageTk.PhotoImage(image=pil_image)

        # 画像の描画
        self.canvas.delete("all")
        self.canvas.create_image(
                canvas_width / 2,       # 画像表示位置(Canvasの中心)
                canvas_height / 2,                   
                image=self.photo_image  # 表示画像データ
                )

        # disp_image()を10msec後に実行する
        self.after(10, self.disp_image)

    def disp_last_record(self):
        db_last_record = self.database.get_last_record()
        self.last_record="".join([str(item) for item in db_last_record])

        # disp_image()を510msec後に実行する
        self.after(510, self.disp_last_record)



    #on_attendance()とon_leaving()はデータベースを作ってからプログラムを修正する
    def on_attendance(self):
        #"出勤ボタンが押されたときの処理
        name = self.get_and_validate_name()
        #データベースにその名前を登録する
        self.database.insert_record(name, "attendance")

    def on_leaving(self):
        #"退勤ボタンが押されたときの処理
        name = self.get_and_validate_name()
        #データベースにその名前を登録する
        self.database.insert_record(name, "leaving")


    def on_closing(self):
        #アプリ終了時にメモリを解放する処理
        self.camera_unit.close()
        self.database.close()
        self.window.destroy()


# アプリケーションの起動
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
