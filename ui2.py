import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk, ImageOps  # 画像データ用
from picamera2.picamera2 import Picamera2



class AttendanceApp:

    def __init__(self, window):
        self.window = window
        self.window.title("勤怠管理システム")

        # 1. カメラの初期化
        self.picam2 = Picamera2()
        self.picam2.start()
        #　カメラの映像を取得するための変数を設定
        self.capture=self.picam2.capture_array()

        # 2. 全体のレイアウト設定（左右のフレームを作成）
        self.left_frame = tk.Frame(window)
        self.left_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.right_frame = tk.Frame(window)
        self.right_frame.pack(
            side=tk.RIGHT, padx=20, pady=20, fill=tk.Y, expand=True
        )

        # 3. 左フレーム：カメラ映像を表示する空のCanvasを作成
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

        # 6. 映像更新ループの開始
        self.disp_image()

        # 7. ウィンドウが閉じられたときの終了処理を登録
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)


    #顔の推定値はこれに渡す
    def get_name_text(self, text):
        """顔から推定されたテキストを取得し、空白を除去して返す"""
        self.name_text = text
        return text.strip()

    def disp_image(self):
        '''画像をCanvasに表示する'''

        # フレーム画像の取得
        frame = self.capture
    
        # BGR→RGB変換
        cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # NumPyのndarrayからPillowのImageへ変換
        pil_image = Image.fromarray(cv_image)

        # キャンバスのサイズを取得
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

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


    #on_attendance()とon_leaving()はデータベースを作ってからプログラムを修正する
    def on_attendance(self):
        """出勤ボタンが押されたときの処理"""
        name = self.get_and_validate_name()
        if name:  # 名前が正しく入力されている場合のみ実行
            messagebox.showinfo("記録完了", f"{name}さんの「出勤」を記録しました。")

    def on_leaving(self):
        """退勤ボタンが押されたときの処理"""
        name = self.get_and_validate_name()
        if name:  # 名前が正しく入力されている場合のみ実行
            messagebox.showinfo("記録完了", f"{name}さんの「退勤」を記録しました。")

    def on_closing(self):
        """アプリ終了時にカメラを安全に解放する処理"""
        self.picam2.stop()
        self.picam2.release()
        self.window.destroy()


# アプリケーションの起動
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
