from moviepy.editor import VideoFileClip
import os
import glob

def process_video(input_path, output_folder):
    # Tạo thư mục đầu ra chính
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Tải video và loại bỏ âm thanh
    video = VideoFileClip(input_path).without_audio()
    duration = video.duration
    print(f"Đã tải video thành công. Thời lượng: {duration:.2f} giây")

    # Xác định tên video và tạo thư mục con cho nó
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    # Thư mục con cho video hiện tại, vd: folder_chunk/DN39s
    os.makedirs(output_folder, exist_ok=True)

    # Chia nhỏ video thành các đoạn 60 giây
    chunk_duration = 20
    start_time = 0
    chunk_count = 0

    while start_time < duration:
        end_time = min(start_time + chunk_duration, duration)
        chunk_count += 1
        print(f"Đang xử lý đoạn {chunk_count} từ {start_time:.2f}s đến {end_time:.2f}s...")

        # Cắt đoạn video
        chunk = video.subclip(start_time, end_time)

        # Thay đổi kích thước và FPS
        processed_chunk = chunk.set_fps(2)

        # Tạo tên file đầu ra
        output_path = os.path.join(
            output_folder,
            f'{base_name}_chunk_{int(start_time)}_{int(end_time)}.mp4'
        )

        # Lưu file
        processed_chunk.write_videofile(output_path,
                                        codec='libx264')

        print(f"Đã lưu đoạn {chunk_count} vào: {output_path}")

        start_time = end_time

    video.close()
    print("Video processing complete!")


def clear_memory(video_chunk, memory):
    # Xóa memory
    try:
        os.remove(memory)
        print('Đã xóa memory!')
    except FileNotFoundError:
        pass
    except PermissionError as e:
        print(f"CẢNH BÁO: Không thể xóa file {memory}. Lỗi: {e}")
        pass

    # Xóa video_chunk
    try:
        # Tạo mẫu tìm kiếm cho tất cả các tệp .mp4 trong thư mục
        sample_file = os.path.join(video_chunk, "*.mp4")
        # Tìm tất cả các tệp khớp với mẫu
        video_paths = glob.glob(sample_file)
        # Lặp qua danh sách và xóa từng tệp
        for video in video_paths:
            os.remove(video)
            print(f"Đã xóa: {video}")
    except FileNotFoundError:
        pass
    except PermissionError as e:
        print(f"CẢNH BÁO: Không thể xóa file {memory}. Lỗi: {e}")
        pass
