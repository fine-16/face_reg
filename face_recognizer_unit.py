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

        best_person = ""
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

        print(best_person)

        return best_person
