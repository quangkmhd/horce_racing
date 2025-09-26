import streamlit as st
import os
from video_processing import process_video, clear_memory
from model import summarize

# Hàm để tải và tiêm CSS
def local_css(file_name):
    # Thay đổi: Thêm tham số encoding='utf-8'
    with open(file_name, encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
# Tải CSS từ file
local_css("style.css")

# --- Cấu hình trang ---
st.set_page_config(
    layout="wide",
    page_title="Video Summary",
    page_icon="🎬"
)

# --- Tiêu đề chính ---
st.title("🎬 Horse racing video summary")

# --- Chia layout làm 2 cột ---
col1, col2 = st.columns([1, 1], gap="large")

# --- Cột trái: Nhập và Hiển thị Video ---
with col1:
    st.header("Input Video 📹")

    # Biến để kiểm tra liệu video đã được cung cấp chưa
    video_input_provided = False

    video_to_display = None


    uploaded_file = st.file_uploader(
        "Kéo thả file video vào đây hoặc nhấp để chọn file:",
        type=["mp4", "avi", "mov"],
        accept_multiple_files=False
    )
    if uploaded_file:
        st.success("Video đã được tải lên thành công!")
        video_input_provided = True
        video_to_display = uploaded_file

    # Hiển thị video đã được nhập
    if video_to_display:
        st.video(video_to_display)


# --- Cột phải: Nội dung Tóm tắt ---
with col2:
    st.header("Nội dung Tóm tắt 📝")

    # Placeholder ban đầu để hiển thị thông báo
    summary_placeholder = st.empty()
    summary_placeholder.info("Vui lòng nhập video ở cột bên trái để xem nội dung tóm tắt.")

    # Logic xử lý và tạo tóm tắt
    if video_input_provided and video_to_display:
        with st.spinner("Đang xử lý video và tạo tóm tắt... ⏳"):
            # Lưu video input vào bộ nhớ
            os.makedirs(os.path.dirname('horce_racing/folder_videos/video.mp4'), exist_ok=True)
            with open('horce_racing/folder_videos/video.mp4', "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Cắt nhỏ video thành nhiều chunk
            process_video('horce_racing/folder_videos/video.mp4', 'horce_racing/folder_videos/folder_chunk')

            # Gọi hàm summarize từ module model.py
            summary = summarize('horce_racing/folder_videos/folder_chunk')
            clear_memory('horce_racing/folder_videos/folder_chunk', 'horce_racing/memory/folder_chunk_memory.json') 

            # Cập nhật placeholder với nội dung tóm tắt
            summary_placeholder.success("Tóm tắt đã sẵn sàng!")
            # Cuộn nội dung nếu quá dài
            st.markdown(
                f"""
                <div class="scrollable-box">
                    {summary}
                </div> 
                """,
                unsafe_allow_html=True
            )
            st.button("Rerun")

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️")
