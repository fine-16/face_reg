import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk, ImageOps  # 画像データ用
from picamera2.picamera2 import Picamera2

picam2 = Picamera2()
picam2.start()

class AttendanceApp:

    def __init__(self, window):
        self.window = window
        self.window.title("勤怠管理システム")

        # 1. カメラの初期化
        self.cap = cv2.VideoCapture(0)

        # 2. 全体のレイアウト設定（左右のフレームを作成）
        self.left_frame = tk.Frame(window)
        self.left_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.right_frame = tk.Frame(window)
        self.right_frame.pack(
            side=tk.RIGHT, padx=20, pady=20, fill=tk.Y, expand=True
        )

        # 3. 左フレーム：カメラ映像を表示する空のCanvasを作成
        self.canvas = tk.Canvas(self.left_frame)
        # Canvasにマウスイベント（左ボタンクリック）の追加
        self.canvas.bind('<Button-1>', self.canvas_click)
        # Canvasを配置
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.capture=picam2.capture_array()
        self.disp_id = None

        # 4. 右フレーム：名前「入力欄」への変更
        self.name_title_label = tk.Label(
            self.right_frame, text="【お名前を入力してください】"
        )
        self.name_title_label.pack(pady=(20, 5))

        # ★ tk.Label から tk.Entry に変更
        self.name_entry = tk.Entry(
            self.right_frame, width=15, justify="center"
        )
        self.name_entry.pack(pady=(0, 40))

        # 初期値として「山田 太郎」と入力された状態にする（空欄から始めたい場合は削除してください）
        self.name_entry.insert(0, "山田 太郎")

        # 5. 右フレーム：出勤・退勤ボタン
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
        self.update_video()

        # 7. ウィンドウが閉じられたときの終了処理を登録
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)


    def canvas_click(self, event):
        '''Canvasのマウスクリックイベント'''

        if self.disp_id is None:
            # 動画を表示
            self.disp_image()
        else:
            # 動画を停止
            self.after_cancel(self.disp_id)
            self.disp_id = None


    def update_video(self):
        """カメラからフレームを取得してTkinter用に変換し、表示を更新する関数"""
        ret, frame = self.cap.read()
        if ret:
            cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv2_image)
            self.photo = ImageTk.PhotoImage(image=pil_image)
            self.video_label.config(image=self.photo)

             # カメラ画像を取得
   

        self.window.after(15, self.update_video)

    def disp_image(self):
        '''画像をCanvasに表示する'''

        # フレーム画像の取得
        ret, frame = self.capture.read()
    
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
        self.disp_id = self.after(10, self.disp_image)

    def get_and_validate_name(self):
        """入力された名前を取得し、空欄チェックを行う共通関数"""
        # ★ .get() でEntry内の文字列を取得
        name = self.name_entry.get().strip()

        if not name:
            messagebox.showwarning("入力エラー", "名前が入力されていません。")
            return None
        return name

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
        self.cap.release()
        self.window.destroy()


# アプリケーションの起動
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
