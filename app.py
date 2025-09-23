import streamlit as st
import time
import google.generativeai as genai

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
            # Bắt đầu Code get API bên dưới: input video

            # Lấy API key từ secrets
            api_key = st.secrets["GEMINI_API_KEY"]
            # Cấu hình API key
            genai.configure(api_key=api_key)
            
            # myfile = client.files.upload(file="C:/Users/admin/Downloads/video_chunk_1.mp4")
            myfile = genai.upload_file(
                path=uploaded_file,
                mime_type=uploaded_file.type
            )
            time.sleep(20)
            prompt = """
You are a professional horse racing commentator. Analyze the image or video frame and generate vivid, energetic, and realistic live commentary.Your output should be structured in segments, each corresponding to a key moment in the race, as if you are narrating in real-time.
For each segment (e.g., 00:01, 00:10, 00:20...), describe:
The positions and movements of the horses (use visible numbers or names).
The actions, posture, and strategy of the jockeys (e.g., leaning in, urging the horse, holding back).
Any dramatic moments such as overtakes, surges, or struggles.
Use a tone that builds excitement and tension, especially as the race progresses.
Format your output like this:
[00:01] Number 3 bursts out of the gate! The jockey in red is urging the horse forward with a strong whip motion.
<Space>
[00:10] Number 7 is gaining ground on the outside—its jockey crouched low, eyes locked on the leader.
<Space>
[00:20] The jockey on Number 5 is holding back slightly, possibly waiting for a final sprint. Smart strategy!
Assume the audience is watching live and understands basic horse racing. Keep each segment short, thrilling, and visually descriptive, like a real sports broadcast.
"""
            model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
            response = model.generate_content(
                contents=[myfile, prompt]
            )
            example_summary = (response.text)

            # Kết thúc code get API

            # Cập nhật placeholder với nội dung tóm tắt
            summary_placeholder.success("Tóm tắt đã sẵn sàng!")
            st.markdown(f"<p style='white-space: pre-wrap;'>{example_summary}</p>", unsafe_allow_html=True)
            st.button("Rerun")

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️")
