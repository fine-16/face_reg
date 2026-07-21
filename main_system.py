'''
#CameraUnitのためのライブラリ
from picamera2.picamera2 import Picamera2
import cv2
from PIL import Image

#Databaseのためのライブラリ
import sqlite3


#FaceRecognizerのためのライブラリ
import os
import numpy as np
import onnx
import onnxruntime as ort
from PIL import Image

#AttendanceAPPのためのライブラリ
import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk, ImageOps  # 画像データ用
from picamera2.picamera2 import Picamera2
'''

#整理したライブラリ
from picamera2.picamera2 import Picamera2
import cv2

import sqlite3

import os
import numpy as np
import onnx
import onnxruntime as ort

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps  # 画像データ用


#最後にclose忘れない<-AttendanceAPPで実装済み
class CameraUnit:

    def __init__(self):
        # カメラの初期化
        self.picam2 = Picamera2()
        self.picam2.start()

    #PILの状態で返す
    def get_frame(self):
        # カメラの映像を取得
        self.capture=self.picam2.capture_array()
        frame = self.capture
        # BGR→RGB変換
        cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # NumPyのndarrayからPillowのImageへ変換
        self.pil_image = Image.fromarray(cv_image)

        return self.pil_image

    def close(self):
        # カメラの停止
        self.picam2.close()

#最後にclose忘れない<-AttendanceAPPで実装済み
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('attendance.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        # テーブルが存在しない場合は作成
        #ここでタイムスタンプはJTCになっている
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (datetime('now', 'localtime')),      
                name TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    
    def insert_record(self, name, status):
        # レコードを挿入
        self.cursor.execute('''
            INSERT INTO attendance (name, status)
            VALUES (?, ?)
        ''', (name, status))
        self.conn.commit()

    def get_last_record(self):
        # 最後のレコードを取得
        self.cursor.execute('''
            SELECT * FROM attendance ORDER BY id DESC LIMIT 1
        ''')
        return self.cursor.fetchone()

    def export_csv(self, filename):
        # CSVファイルにエクスポート
        self.cursor.execute('''
            SELECT * FROM attendance
        ''')
        records = self.cursor.fetchall()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("id,timestamp,name,status\n")
            for record in records:
                f.write(','.join(map(str, record)) + '\n')

    def delete_table(self):
        # テーブルを削除
        self.cursor.execute('''
            DROP TABLE IF EXISTS attendance
        ''')
        self.conn.commit()
    
    def close(self):
        # データベース接続を閉じる
        self.cursor.close()
        self.conn.close()


#recognize_faceの部分を後で適切に書き換える　特にquery_imageと出力の部分
class FaceRecognizer:
    #使う写真はPNGで224px×224pxにリサイズしておくこと
    
    def __init__(self, model_name="JAPANESE_FACE_v1.onnx"):
        #----------------------------
        # モデル読込
        # ----------------------------
        self.model_name = model_name
        self.onnx_model = onnx.load(self.model_name)
        self.ort_session = ort.InferenceSession(self.model_name)
        self.input_name = self.onnx_model.graph.input[0].name

   
   #pilの状態で受け取る
    def get_embedding(self, pil_image):
         # ----------------------------
         # 特徴量抽出
         # ----------------------------

        # 0. 画像の読み込み (PIL)
        img = pil_image
    
        # 1. transforms.Resize((224, 224)) の再現
        # ※PILのImage.BILINEAR（またはImage.Resampling.BILINEAR）がデフォルトの挙動です
        img_resized = img.resize((224, 224), resample=Image.BILINEAR)
        # 2. transforms.ToTensor() の再現
        # [H, W, C] 且つ 0〜255 の整数から、[C, H, W] 且つ 0.0〜1.0 の浮動小数点に変換します
        img_np = np.array(img_resized, dtype=np.float32) / 255.0  # 0~1に正規化
        img_tensor = img_np.transpose(2, 0, 1)                     # [H,W,C] -> [C,H,W]
    
        # 3. transforms.Normalize(mean, std) の再現
        # 各チャンネル（R, G, B）に対して (x - mean) / std を計算します
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(3, 1, 1)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(3, 1, 1)
    
        img_normalized = (img_tensor - mean) / std

        image = img_normalized[None]

        embedding = self.ort_session.run(
            None,
            {self.input_name: image}
        )[0]

        embedding = embedding.flatten()
        embedding /= np.linalg.norm(embedding)

        return embedding
 
    def cosine_similarity(self, v1, v2):
       # ----------------------------
       # コサイン類似度
       # ----------------------------

        return np.dot(v1, v2)
  
    def percentage(self,cos_sim):
        # ----------------------------
        # 百分率（元の式を利用）
        # ----------------------------

        return round(
            -23.71 * cos_sim ** 2
            + 49.98 * cos_sim
            + 73.69,
            2
        )
  
  #best_personを返す
    def recognize_face(self, pil_image, feature_dir="saved_feature"):
        #============================
        # 顔認識のメイン処理
        #認識した顔の名前を返す
        #============================

        # ============================
        # カメラから受け取った画像
        # ============================

        query_embedding = self.get_embedding(pil_image)

        # ============================
        # 登録人物
        # ============================
        feature_dir = "saved_feature"

        best_person = "Unknown"
        best_similarity = -1

        for file in os.listdir(feature_dir):

            if not file.lower().endswith(".npy"):
                continue

            path = os.path.join(feature_dir, file)

            embedding = np.load(path)

            sim = self.cosine_similarity(query_embedding, embedding)

            print(f"{os.path.splitext(file)[0]:15s} : {self.percentage(sim)}%")

            if sim > best_similarity:
                best_similarity = sim
                best_person = os.path.splitext(file)[0]
            
        if self.percentage(best_similarity) < 82: #個々の値は何％だったらその人とするかの値　これがないとヒトじゃなくても反応する
            best_person = "Unknown"

        print(best_person)

        return best_person


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
        self.name_label = tk.Label(
            self.right_frame, text= self.name_text
        )
        self.name_label.pack(pady=(20, 5))

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
            self.right_frame, text= self.last_record, background='#FFFFFF'
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
        self.name_label["text"] = "認識した人 : " + best_person_name

        # disp_image()を1000msec後に実行する
        self.window.after(1000, self.disp_best_person_name)


    def disp_image(self):
        #画像をCanvasに表示する

        

        # キャンバスのサイズを取得
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        #pilimageをframeに渡す
        pil_image = self.camera_unit.get_frame() 
        bgr_array = np.array(pil_image)[:,:,::-1]
        img_bgr = Image.fromarray(bgr_array)
        #pil_image = cv2.cvtColor(pil_image, cv2.COLOR_BGR2RGB)

        # 画像のアスペクト比（縦横比）を崩さずに指定したサイズ（キャンバスのサイズ）全体に画像をリサイズする
        pil_image = ImageOps.pad(img_bgr, (canvas_width, canvas_height))

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
        self.window.after(10, self.disp_image)

    def disp_last_record(self):
        self.last_record = self.database.get_last_record()
        # self.last_record="".join([str(item) for item in db_last_record])
        self.last_record_label["text"] = self.last_record

        # disp_image()を1000msec後に実行する
        self.window.after(1000, self.disp_last_record)



    #on_attendance()とon_leaving()はデータベースを作ってからプログラムを修正する
    def on_attendance(self):
        #"出勤ボタンが押されたときの処理
        #データベースにその名前を登録する
        self.database.insert_record(self.name_text, "attendance")

    def on_leaving(self):
        #"退勤ボタンが押されたときの処理
        #データベースにその名前を登録する
        self.database.insert_record(self.name_text, "leaving")


    def on_closing(self):
        #アプリ終了時にメモリを解放する処理
        self.camera_unit.close()
        self.database.close()
        self.window.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    camera_unit = CameraUnit()
    face_recognizer = FaceRecognizer()
    database = Database() 
    app = AttendanceApp(root,camera_unit,face_recognizer,database)
    root.mainloop()
   