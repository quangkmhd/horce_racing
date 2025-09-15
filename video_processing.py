from moviepy.editor import VideoFileClip
import os

def process_video(input_path, output_folder='output_videos'):
    # Tạo thư mục đầu ra
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Tải video và loại bỏ âm thanh
    video = VideoFileClip(input_path).without_audio()
    duration = video.duration
    print(f"Đã tải video thành công. Thời lượng: {duration:.2f} giây")

    # Chia nhỏ video thành các đoạn 60 giây
    chunk_duration = 60
    start_time = 0
    chunk_count = 0

    while start_time < duration:
        end_time = min(start_time + chunk_duration, duration)
        chunk_count += 1
        print(f"Đang xử lý đoạn {chunk_count} từ {start_time:.2f}s đến {end_time:.2f}s...")

        # Cắt đoạn video
        chunk = video.subclip(start_time, end_time)

        # Thay đổi kích thước và FPS
        processed_chunk = chunk.resize(newsize=(644, 392)).set_fps(4)

        # Tạo tên file đầu ra
        output_path = os.path.join(output_folder, f'video_chunk_{chunk_count}.mp4')

        # Lưu file
        processed_chunk.write_videofile(output_path,
                                        codec='libx264')

        print(f"Đã lưu đoạn {chunk_count} vào: {output_path}")

        start_time = end_time

    video.close()
    print("Done!")