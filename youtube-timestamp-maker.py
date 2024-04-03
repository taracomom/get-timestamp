import cv2
import streamlit as st
from PIL import Image
import tempfile
import zipfile  # 追加
from io import BytesIO
import base64
import streamlit.components.v1 as components

st.set_page_config(page_title="チャプター作成お助けツール", page_icon=":camera:", layout="wide")

def ms_to_hms(ms):
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    hours = int((ms / (1000 * 60 * 60)) % 24)
    return f"{hours:02d}-{minutes:02d}-{seconds:02d}"

def process_video(video_file, max_frames, threshold):
    progress_message = st.info("動画を処理しています...")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(video_file.read())
        temp_name = tmp.name

    cap = cv2.VideoCapture(temp_name)
    
    if not cap.isOpened():
        st.error(f"動画ファイル{video_file.name}が開けませんでした。")
        return
    
    prev_frame_gray = None
    output_images = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count >= max_frames:
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame_gray is not None:
            diff = cv2.absdiff(prev_frame_gray, frame_gray)
            diff_avg = diff.mean()

            if diff_avg > threshold:
                timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                timestamp_hms = ms_to_hms(timestamp_ms)
                
                # PIL Imageに変換
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                
                # 画像を表示
                if frame_count % 3 == 0:
                    cols = st.columns(3)
                cols[frame_count % 3].image(image, caption=timestamp_hms, use_column_width=True)
                
                # 出力リストに追加
                output_images.append((timestamp_hms, image))

                frame_count += 1

        prev_frame_gray = frame_gray

    cap.release()

    if not output_images:
        st.warning("フレームが抽出されませんでした。")
        return

    # 画像を一時的に保存してダウンロードリンクを生成
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for timestamp, image in output_images:
            image_bytes = BytesIO()
            image.save(image_bytes, format="JPEG")
            image_bytes.seek(0)
            zip_file.writestr(f"{timestamp}.jpg", image_bytes.getvalue())

    zip_bytes = zip_buffer.getvalue()
    st.markdown(get_binary_file_downloader_html(zip_bytes, file_label="完了しました！フレーム画像のダウンロードはこちら"), unsafe_allow_html=True)

    # メッセージを非表示にする
    progress_message.empty()

def get_binary_file_downloader_html(bin_file, file_label='File'):
    """
    Create a downloader for a binary file string.

    Parameters:
    - bin_file: Binary file data as bytes
    - file_label: Text label to use for the download link

    Returns:
    - HTML string with download link
    """
    bin_str = base64.b64encode(bin_file).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}.zip">{file_label}</a>'
    return href

def main():
    st.title("チャプター作成お助けツール")

    # 説明を追加
    st.write("アップロードした動画の中でフレームに大きく変化があった箇所のフレーム画像とタイムスタンプを取得し、表示します。")
    st.write("スライドを使った動画のチャプター作成に便利です。JPGのダウンロードもできます。")

    # 名前とTwitterリンクを表示するHTMLコンテンツ
    footer_html = """
    <div style="position: fixed; bottom: 10px; left: 10px; background-color: white; padding: 10px; border-radius: 10px;">
        <a href="https://twitter.com/chibinftcom" target="_blank">作成者：うみの（AIとNFTの専門家）</a>
    </div>
    """

    # Streamlitアプリにフッターを埋め込む
    components.html(footer_html, height=100)

    # 閾値の設定

    threshold = st.sidebar.slider("フレームの変化の閾値", 1, 50, 20)

    max_frames = 100  # デフォルトの最大フレーム数

    video_file = st.file_uploader("動画ファイルをアップロードしてください", type=["mp4", "avi", "mov"])

    if video_file is not None:
        if not video_file.name.lower().endswith((".mp4", ".avi", ".mov")):
            st.error("サポートされていない動画ファイル形式です。")
        else:
            process_video(video_file, max_frames, threshold)


if __name__ == "__main__":
    main()
