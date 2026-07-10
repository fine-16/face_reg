from picamera2.picamera2 import Picamera2
import cv2

# Picamera2を初期化
picam2 = Picamera2()

# Camera Module 2の最大解像度（3280×2464）を使用
config = picam2.create_preview_configuration(
    main={"size": (3280, 2464)}
)

# 設定を反映
picam2.configure(config)

# カメラを起動
picam2.start()

while True:

    # カメラ画像を取得
    frame = picam2.capture_array()

    # OpenCVで扱えるBGR形式へ変換
    frame = cv2.cvtColor(
        frame,
        cv2.COLOR_RGB2BGR
    )

    # 表示幅（スマホ向け）
    display_width = 355

    # 元画像サイズ取得
    h, w = frame.shape[:2]

    # 縦横比を維持して高さを計算
    display_height = int(
        h * display_width / w
    )

    # 表示用に縮小
    display = cv2.resize(
        frame,
        (display_width, display_height)
    )

    # カメラ映像を表示
    cv2.imshow(
        "Camera",
        display
    )

    # Escキーで終了
    if cv2.waitKey(1) == 27:
        break

# OpenCVウィンドウを閉じる
cv2.destroyAllWindows()

# カメラ停止
picam2.stop()