import os
import shutil

import numpy as np
import onnx
import onnxruntime as ort
from PIL import Image


#使う写真はPNGで224px×224pxにリサイズしておくこと
#写真の名前を本名.pngにしてもらう（空欄を入れない）
#使う写真をprepare_queryに入れる。その際に前にあった写真は消す


# ----------------------------
# モデル読込
# ----------------------------

model_name = "JAPANESE_FACE_V2.onnx"
onnx_model = onnx.load(model_name)
ort_session = ort.InferenceSession(model_name)

input_name = onnx_model.graph.input[0].name

# ----------------------------
# 特徴量抽出
# ----------------------------
def get_embedding(image_path):


     # 0. 画像の読み込み (PIL)
    # torchvision.transforms は内部で PIL Image をベースに処理を行います
    img = Image.open(image_path).convert('RGB')
    
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

    embedding = ort_session.run(
        None,
        {input_name: image}
    )[0]

    embedding = embedding.flatten()
    embedding /= np.linalg.norm(embedding)

    return embedding



#============================
#アプリのメイン処理
#ndarray形式で保存を行う
#保存できたファイルをprepare_queryからregistered_photosに移動する
#============================

if __name__ == "__main__":
    # ============================
    # queryに入っているファイルを特徴量に変換して変換できた写真はregistered_photosに移動する
    # ============================

    for file in os.listdir("query"):
        if file.endswith(".png"):
            query_image = os.path.join("query", file)
            query_embedding = get_embedding(query_image)

            output_dir = "saved_feature"
            file_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.npy")
            np.save(file_path, query_embedding)

            print("保存完了:", file_path)

            shutil.move(query_image, 'registered_photos')  # 登録済み写真フォルダに移動
    