import streamlit as st
import os
from video_processing import process_video
from model import summarize

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

    # Lựa chọn phương thức nhập video
    video_source = st.radio(
        "**Chọn cách bạn muốn cung cấp video:**",
        ('Tải lên File', 'Nhập URL'),
        help="Sử dụng 'Tải lên File' cho các video có sẵn trên máy tính của bạn hoặc 'Nhập URL' cho các video trực tuyến."
    )

    video_to_display = None

    if video_source == 'Tải lên File':
        uploaded_file = st.file_uploader(
            "Kéo thả file video vào đây hoặc nhấp để chọn file:",
            type=["mp4", "avi", "mov"],
            accept_multiple_files=False
        )
        if uploaded_file:
            st.success("Video đã được tải lên thành công!")
            video_input_provided = True
            video_to_display = uploaded_file

    elif video_source == 'Nhập URL':
        video_url = st.text_input(
            "Dán URL trực tiếp của video vào đây:",
            help="**Quan trọng:** Vui lòng chỉ dán URL **trực tiếp** đến file video (ví dụ: `https://domain.com/video.mp4`). URL của trang web (như YouTube) sẽ không hoạt động."
        )
        if video_url:
            st.info("Đang xử lý URL...")
            # Kiểm tra đơn giản để xem nó có giống URL không
            if "." in video_url and ("/" in video_url or "://" in video_url):
                video_input_provided = True
                video_to_display = video_url
            else:
                st.error("Định dạng URL không hợp lệ. Vui lòng kiểm tra lại.")

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
            os.makedirs(os.path.dirname('/input_video/video.mp4'), exist_ok=True)
            with open('/input_video/video.mp4', "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Cắt nhỏ video thành nhiều chunk
            process_video('/input_video/video.mp4')

            # Gọi hàm summarize từ module model.py
            summary = summarize('/input_video')

            # Cập nhật placeholder với nội dung tóm tắt
            summary_placeholder.success("Tóm tắt đã sẵn sàng!")
            st.markdown(f"<p style='white-space: pre-wrap;'>{summary}</p>", unsafe_allow_html=True)
            st.button("Rerun")

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️")
