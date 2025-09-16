#!/usr/bin/env python3
"""
Horse Racing Commentary Generator - Main Application
Orchestrates the complete pipeline from video processing to SRT output
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.video_processor import VideoProcessor, VideoClip
from src.event_detector import EventDetector, RaceEvent
from src.memory_system import MemorySystem
from src.commentary_generator import CommentaryGenerator, Commentary
from src.srt_generator import SRTGenerator


class HorseRacingCommentaryGenerator:
    """Main orchestrator for the horse racing commentary generation system"""
    
    def __init__(self, config: dict = None):
        """
        Initialize the commentary generation system
        
        Args:
            config: Configuration dictionary with system parameters
        """
        self.config = config or {}
        
        # Initialize components
        self.video_processor = VideoProcessor(
            output_dir=self.config.get('output_dir', 'output'),
            clip_duration=self.config.get('clip_duration', 3.0)
        )
        
        self.event_detector = EventDetector(
            model_path=self.config.get('qwen_model_path', 'models/qwen2.5-vl-7b-instruct')
        )
        
        self.commentary_generator = CommentaryGenerator()
        self.srt_generator = SRTGenerator()
        
        print("🐎 Horse Racing Commentary Generator initialized")
        print(f"📁 Output directory: {self.config.get('output_dir', 'output')}")
        print(f"⏱️  Clip duration: {self.config.get('clip_duration', 3.0)}s")
    
    def process_video(self, video_path: str, output_name: str = None) -> str:
        """
        Process a complete video through the entire pipeline
        
        Args:
            video_path: Path to input MP4 video
            output_name: Base name for output files (optional)
            
        Returns:
            Path to generated SRT file
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Generate output name if not provided
        if not output_name:
            output_name = Path(video_path).stem
        
        output_dir = Path(self.config.get('output_dir', 'output'))
        
        print(f"\n🎬 Processing video: {video_path}")
        print(f"📝 Output name: {output_name}")
        print("=" * 50)
        
        # Step 1: Video Processing
        print("\n📹 Step 1: Processing video into clips...")
        start_time = time.time()
        
        clips = self.video_processor.process_video(video_path)
        
        processing_time = time.time() - start_time
        print(f"✅ Generated {len(clips)} clips in {processing_time:.2f}s")
        
        # Step 2: Event Detection
        print("\n🔍 Step 2: Detecting racing events...")
        start_time = time.time()
        
        events = self.event_detector.analyze_video_clips(clips)
        
        detection_time = time.time() - start_time
        print(f"✅ Detected {len(events)} events in {detection_time:.2f}s")
        
        # Save events for debugging
        events_file = output_dir / f"{output_name}_events.json"
        self.event_detector.save_events_to_json(events, str(events_file))
        
        # Step 3: Commentary Generation
        print("\n🎙️  Step 3: Generating commentary...")
        start_time = time.time()
        
        # Add sample horse data if needed
        self.commentary_generator.memory_system.add_sample_horse_data()
        
        commentaries = self.commentary_generator.generate_commentary_for_events(events)
        
        generation_time = time.time() - start_time
        print(f"✅ Generated {len(commentaries)} commentaries in {generation_time:.2f}s")
        
        # Save commentaries for debugging
        commentary_file = output_dir / f"{output_name}_commentaries.json"
        self.commentary_generator.save_commentaries_to_json(commentaries, str(commentary_file))
        
        # Step 4: SRT Generation
        print("\n📄 Step 4: Generating subtitle files...")
        start_time = time.time()
        
        srt_base_path = str(output_dir / output_name)
        self.srt_generator.generate_multi_format_subtitles(commentaries, srt_base_path)
        
        srt_time = time.time() - start_time
        print(f"✅ Generated subtitle files in {srt_time:.2f}s")
        
        # Final summary
        srt_file = f"{srt_base_path}.srt"
        print("\n🎉 Processing completed successfully!")
        print("=" * 50)
        print(f"📊 Summary:")
        print(f"   • Video clips: {len(clips)}")
        print(f"   • Events detected: {len(events)}")
        print(f"   • Commentaries generated: {len(commentaries)}")
        print(f"📁 Output files:")
        print(f"   • SRT subtitles: {srt_file}")
        print(f"   • WebVTT subtitles: {srt_base_path}.vtt")
        print(f"   • Text transcript: {srt_base_path}_transcript.txt")
        print(f"   • Events data: {events_file}")
        print(f"   • Commentary data: {commentary_file}")
        
        return srt_file
    
    def batch_process_videos(self, video_dir: str, pattern: str = "*.mp4"):
        """
        Process multiple videos in a directory
        
        Args:
            video_dir: Directory containing video files
            pattern: File pattern to match (default: *.mp4)
        """
        video_path = Path(video_dir)
        if not video_path.exists():
            raise FileNotFoundError(f"Video directory not found: {video_dir}")
        
        video_files = list(video_path.glob(pattern))
        if not video_files:
            print(f"No video files found matching pattern: {pattern}")
            return
        
        print(f"🎬 Found {len(video_files)} video files to process")
        
        for i, video_file in enumerate(video_files, 1):
            print(f"\n📹 Processing video {i}/{len(video_files)}: {video_file.name}")
            try:
                self.process_video(str(video_file), video_file.stem)
            except Exception as e:
                print(f"❌ Error processing {video_file.name}: {str(e)}")
                continue
        
        print(f"\n🎉 Batch processing completed: {len(video_files)} videos processed")
    
    def get_video_info(self, video_path: str):
        """Display video information"""
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return
        
        try:
            info = self.video_processor.get_video_info(video_path)
            print(f"\n📹 Video Information: {Path(video_path).name}")
            print("=" * 40)
            print(f"Duration: {info['duration']:.2f} seconds")
            print(f"FPS: {info['fps']:.2f}")
            print(f"Resolution: {info['width']}x{info['height']}")
            print(f"Total frames: {info['frame_count']}")
            
        except Exception as e:
            print(f"❌ Error reading video info: {str(e)}")


def create_config_from_args(args) -> dict:
    """Create configuration dictionary from command line arguments"""
    config = {
        'output_dir': args.output_dir,
        'clip_duration': args.clip_duration,
        'qwen_model_path': args.model_path
    }
    return config


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(
        description="Horse Racing Commentary Generator - AI-powered race commentary from video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single video
  python main.py process video.mp4
  
  # Process with custom output directory
  python main.py process video.mp4 --output-dir my_output
  
  # Process multiple videos
  python main.py batch /path/to/videos/
  
  # Get video information
  python main.py info video.mp4
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process a single video')
    process_parser.add_argument('video_path', help='Path to input MP4 video file')
    process_parser.add_argument('--output-name', help='Base name for output files')
    process_parser.add_argument('--output-dir', default='output', 
                               help='Output directory (default: output)')
    process_parser.add_argument('--clip-duration', type=float, default=3.0,
                               help='Duration of each clip in seconds (default: 3.0)')
    process_parser.add_argument('--model-path', default='models/qwen2.5-vl-7b-instruct',
                               help='Path to Qwen2.5-VL model')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Process multiple videos')
    batch_parser.add_argument('video_dir', help='Directory containing video files')
    batch_parser.add_argument('--pattern', default='*.mp4',
                             help='File pattern to match (default: *.mp4)')
    batch_parser.add_argument('--output-dir', default='output',
                             help='Output directory (default: output)')
    batch_parser.add_argument('--clip-duration', type=float, default=3.0,
                             help='Duration of each clip in seconds (default: 3.0)')
    batch_parser.add_argument('--model-path', default='models/qwen2.5-vl-7b-instruct',
                             help='Path to Qwen2.5-VL model')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Display video information')
    info_parser.add_argument('video_path', help='Path to video file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'process':
            config = create_config_from_args(args)
            generator = HorseRacingCommentaryGenerator(config)
            generator.process_video(args.video_path, args.output_name)
            
        elif args.command == 'batch':
            config = create_config_from_args(args)
            generator = HorseRacingCommentaryGenerator(config)
            generator.batch_process_videos(args.video_dir, args.pattern)
            
        elif args.command == 'info':
            generator = HorseRacingCommentaryGenerator()
            generator.get_video_info(args.video_path)
    
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
