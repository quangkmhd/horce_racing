"""
Video Processing Module for Horse Racing Commentary System
Handles video segmentation into clips and frame extraction
"""

import cv2
import os
from typing import List, Tuple, Dict
from dataclasses import dataclass
import numpy as np
from pathlib import Path


@dataclass
class VideoClip:
    """Represents a video clip with timing information"""
    start_time: float  # seconds
    end_time: float    # seconds 
    clip_id: str      # unique identifier
    frame_path: str   # path to extracted frame
    clip_path: str    # path to video clip file


class VideoProcessor:
    """Processes horse racing videos into analyzable clips"""
    
    def __init__(self, output_dir: str = "output", clip_duration: float = 3.0):
        """
        Initialize video processor
        
        Args:
            output_dir: Directory to store processed clips and frames
            clip_duration: Duration of each clip in seconds
        """
        self.output_dir = Path(output_dir)
        self.clip_duration = clip_duration
        
        # Create output directories
        self.clips_dir = self.output_dir / "clips"
        self.frames_dir = self.output_dir / "frames"
        self.clips_dir.mkdir(parents=True, exist_ok=True)
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        
    def process_video(self, video_path: str) -> List[VideoClip]:
        """
        Process video into clips and extract representative frames
        
        Args:
            video_path: Path to input MP4 video
            
        Returns:
            List of VideoClip objects with timing and file information
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        # Get video properties
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        cap.release()
        
        print(f"Processing video: {video_path}")
        print(f"Duration: {duration:.2f}s, FPS: {fps}, Total frames: {total_frames}")
        
        # Calculate clip segments
        clips = []
        current_time = 0.0
        clip_index = 0
        
        while current_time < duration:
            end_time = min(current_time + self.clip_duration, duration)
            
            clip_id = f"clip_{clip_index:04d}_{current_time:.1f}_{end_time:.1f}"
            
            # Extract clip
            clip_path = self._extract_clip(video_path, current_time, end_time, clip_id)
            
            # Extract representative frame (middle of clip)
            mid_time = (current_time + end_time) / 2
            frame_path = self._extract_frame(video_path, mid_time, clip_id)
            
            clip = VideoClip(
                start_time=current_time,
                end_time=end_time,
                clip_id=clip_id,
                frame_path=frame_path,
                clip_path=clip_path
            )
            
            clips.append(clip)
            current_time = end_time
            clip_index += 1
            
        print(f"Generated {len(clips)} clips from video")
        return clips
    
    def _extract_clip(self, video_path: str, start_time: float, end_time: float, clip_id: str) -> str:
        """Extract video clip using ffmpeg-python or opencv"""
        output_path = self.clips_dir / f"{clip_id}.mp4"
        
        # Use opencv for clip extraction
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Calculate frame numbers
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (frame_width, frame_height))
        
        # Extract frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        for frame_num in range(start_frame, end_frame):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
                
        cap.release()
        out.release()
        
        return str(output_path)
    
    def _extract_frame(self, video_path: str, timestamp: float, clip_id: str) -> str:
        """Extract a single frame at specified timestamp"""
        output_path = self.frames_dir / f"{clip_id}_frame.jpg"
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Jump to specific frame
        frame_number = int(timestamp * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(str(output_path), frame)
        else:
            print(f"Warning: Could not extract frame at {timestamp}s")
            
        cap.release()
        return str(output_path)
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get basic video information"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
            
        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return info


if __name__ == "__main__":
    # Test the video processor
    processor = VideoProcessor(output_dir="test_output", clip_duration=2.0)
    
    # Example usage
    video_path = "/home/quangnh58/horce_racing/input_video/DN39s.mp4"
    if os.path.exists(video_path):
        clips = processor.process_video(video_path)
        print(f"Processed {len(clips)} clips")
        
        # Print first few clips
        for i, clip in enumerate(clips[:3]):
            print(f"Clip {i}: {clip.start_time:.1f}s - {clip.end_time:.1f}s")
    else:
        print(f"Test video not found at {video_path}")
