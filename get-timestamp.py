import cv2
import os

def ms_to_hms(ms):
    # ミリ秒を時間、分、秒に変換
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    hours = int((ms / (1000 * 60 * 60)) % 24)
    return f"{hours:02d}-{minutes:02d}-{seconds:02d}"

# ユーザーから動画ファイルと出力フォルダのパスを入力してもらう
video_path = input('動画ファイルのフルパスを入力してください: ').strip('"')
output_folder = input('出力フォルダのフルパスを入力してください: ').strip('"')


# 出力フォルダが存在しない場合は作成
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# OpenCVで動画ファイルを読み込む
cap = cv2.VideoCapture(video_path)

# 最初のフレームを読み込む
ret, prev_frame = cap.read()

# グレースケールに変換
prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

while True:
    # 次のフレームを読み込む
    ret, frame = cap.read()
    
    if not ret:
        break  # 動画の最後まで読み込んだら終了
    
    # 現在のフレームをグレースケールに変換
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 前のフレームとの差分を計算
    diff = cv2.absdiff(prev_frame_gray, frame_gray)
    
    # 差分の平均値を計算
    diff_avg = diff.mean()
    
    if diff_avg > 20:  # 差分の閾値は適宜調整
        # 現在のタイムスタンプをミリ秒で取得
        timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        # ミリ秒を時:分:秒の形式に変換し、ファイル名を生成
        timestamp_hms = ms_to_hms(timestamp_ms)
        filename = f"{timestamp_hms}.jpg"
        filepath = os.path.join(output_folder, filename)
        # 現在のフレームをJPEGファイルとして出力
        cv2.imwrite(filepath, frame)
    
    # 現在のフレームを次の比較のために設定
    prev_frame_gray = frame_gray

# 動画ファイルを閉じる
cap.release()
