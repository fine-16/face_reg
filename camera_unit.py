from picamera2.picamera2 import Picamera2
import cv2
from PIL import Image


class CameraUnit:

    def __init__(self):
        # カメラの初期化
        self.picam2 = Picamera2()
        self.picam2.start()


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
        # 2. カメラの停止
        self.picam2.stop()

if __name__ == "__main__":
    camera_unit = CameraUnit()
    try:
        while True:
            frame = camera_unit.get_frame()
            Image.show(frame)
    except KeyboardInterrupt:
        pass
    finally:
        camera_unit.close()