# Face_Recognition
  ラズベリーパイ３Bで動く簡単な顔認証勤怠システムです
  顔を認証してそれをsqliteで保管してグーグルドライブと連携してウェブ上から確認できるようにしました

## インストール
python>=3.12で動くはずです。

- レポジトリをクローン
git clone https://github.com/fine-16/face_reg.git

- ディレクトリ移動
  cd face_reg

- 依存関係のインストール
  以下のバージョンで動きました。
  requires.txtとかだとうまくいかなかったりしたので一つずつ祈りながらインストールしてください
  仮想環境を立てるとカメラの認識がうまくいかなくなります。
  opencv、pillowとかが入ったり入らなかったりします


- バージョン
python == 3.13.5
numpy == 2.2.4
onnx == 1.22.0
onnxruntime == 1.27.0
opencv == 4.10.0
pillow == 11.1.0
picamera2 == 0.3.36
pip == 25.1.1
sqlite3 == 3.46.1
schedule == 1.2.2


## 使用方法
- 1. 初めにqueryフォルダに224px*224pxにかこうしたフルネーム.pngnの写真を入れてください。prepare.pyを動かすとその写真はregistered_photosに移動して特徴量がsaved_featureに入ります。
  
- 2. main.pyを起動する 
- 3. 顔を画像全体に移るようにする
- 4. 出勤または退勤を押す
- 5. 下にタイムスタンプと名前と状態が表示される
- 6. syncプログラムを起動することによってrcloneでグーグルドライブと同期します
  同期の頻度は３０分おきにしてあります
  webページ上から確認できるようにしてあります。

## 注意事項
- 起動と終了が遅いですが何も触らないで待ってください
- フリーズしたらタスクを切ってアプリを再起動してください
- ウェブ上で確認するにはネットにつないでください　なくても動きはします
- Dockerはカメラをうまく認識させられませんでした
- uvで環境構築をしようとしたためtomlとかがくっついていますが、カメラの問題で途中から使ってないので気にしないでください
  
##　謝辞
This project contains code from yKesamaru/FACE01_DEV which is licensed under the Apache License, Version 2.0.
  
# メモ
prepare_systemはqueryフォルダにpngの224px*224pxの写真を入れて実行するとsaved_featureに.npyで保存されて写真はregistered_photosに移動する
この際写真の名前をフルネーム（空欄なし）にしておくことここの名前が勤怠の登録される名前になる
万が一登録する写真を変えるときは名前を全く同じにすること

仮想環境で動かそうとするとカメラを認識しなくなる<-uvで環境構築したけどuvで動かそうとすると動かない

JAPANESE_FACEのライブラリやdlib,torchは使わない　クラッシュする
スワップ領域はひろげたまま　戻したときの動作が分からないからそのまま

prepare_system
main_system
format
からできている
prepareは顔の登録の時に使う
mainが顔認証とデータベース登録と同期
formatはデータベースの消去


起動と終了に時間がめっちゃかかる

ラズパイに余裕がありそうだったら顔の追跡も実装する

ボタンを何かに使いたい
スピーカーも利用したい