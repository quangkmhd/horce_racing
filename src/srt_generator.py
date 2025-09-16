"""
SRT Subtitle Generator for Horse Racing Commentary System
Converts commentary to SRT format with proper timestamps
"""

import os
from typing import List
from dataclasses import dataclass
from pathlib import Path
from src.commentary_generator import Commentary


@dataclass
class SRTEntry:
    """Represents a single SRT subtitle entry"""
    sequence: int
    start_time: str  # Format: HH:MM:SS,mmm
    end_time: str    # Format: HH:MM:SS,mmm
    text: str


class SRTGenerator:
    """Generates SRT subtitle files from commentary data"""
    
    def __init__(self):
        """Initialize SRT generator"""
        pass
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """
        Convert seconds to SRT time format (HH:MM:SS,mmm)
        
        Args:
            seconds: Time in seconds (float)
            
        Returns:
            Formatted time string for SRT
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _format_commentary_text(self, commentary: Commentary) -> str:
        """
        Format commentary text for SRT display
        
        Args:
            commentary: Commentary object
            
        Returns:
            Formatted text for subtitle display
        """
        # Main commentary text
        main_text = commentary.text.strip()
        
        # Add reaction if available and different from main text
        if commentary.reaction and commentary.reaction.strip() != main_text:
            reaction = commentary.reaction.strip()
            formatted_text = f"{main_text}\n<i>{reaction}</i>"
        else:
            formatted_text = main_text
        
        # Add replay indicator if suggested
        if commentary.replay_suggested:
            formatted_text += "\n[REPLAY]"
        
        # Add persona indicator for dramatic effect
        if commentary.persona == "kinh_tinh":
            formatted_text = f"<b>{formatted_text}</b>"
        elif commentary.persona == "chuyen_gia":
            formatted_text = f"<font color=\"blue\">{formatted_text}</font>"
        
        return formatted_text
    
    def generate_srt_from_commentaries(self, commentaries: List[Commentary], output_path: str):
        """
        Generate SRT subtitle file from commentary list
        
        Args:
            commentaries: List of Commentary objects
            output_path: Path to output SRT file
        """
        if not commentaries:
            print("No commentaries provided for SRT generation")
            return
        
        # Sort commentaries by start time
        sorted_commentaries = sorted(commentaries, key=lambda c: c.start_time)
        
        srt_entries = []
        
        for i, commentary in enumerate(sorted_commentaries, 1):
            # Convert times to SRT format
            start_time_srt = self._seconds_to_srt_time(commentary.start_time)
            end_time_srt = self._seconds_to_srt_time(commentary.end_time)
            
            # Format text
            formatted_text = self._format_commentary_text(commentary)
            
            # Create SRT entry
            entry = SRTEntry(
                sequence=i,
                start_time=start_time_srt,
                end_time=end_time_srt,
                text=formatted_text
            )
            
            srt_entries.append(entry)
        
        # Write SRT file
        self._write_srt_file(srt_entries, output_path)
        print(f"Generated SRT file with {len(srt_entries)} entries: {output_path}")
    
    def _write_srt_file(self, entries: List[SRTEntry], output_path: str):
        """Write SRT entries to file"""
        # Create output directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(f"{entry.sequence}\n")
                f.write(f"{entry.start_time} --> {entry.end_time}\n")
                f.write(f"{entry.text}\n\n")
    
    def generate_multi_format_subtitles(self, commentaries: List[Commentary], base_output_path: str):
        """
        Generate multiple subtitle formats (SRT, VTT, etc.)
        
        Args:
            commentaries: List of Commentary objects
            base_output_path: Base path without extension
        """
        # Generate SRT
        srt_path = f"{base_output_path}.srt"
        self.generate_srt_from_commentaries(commentaries, srt_path)
        
        # Generate WebVTT for web players
        vtt_path = f"{base_output_path}.vtt"
        self._generate_vtt_file(commentaries, vtt_path)
        
        # Generate simple text transcript
        txt_path = f"{base_output_path}_transcript.txt"
        self._generate_text_transcript(commentaries, txt_path)
        
        print(f"Generated subtitle files:")
        print(f"  - SRT: {srt_path}")
        print(f"  - WebVTT: {vtt_path}")
        print(f"  - Transcript: {txt_path}")
    
    def _generate_vtt_file(self, commentaries: List[Commentary], output_path: str):
        """Generate WebVTT subtitle file"""
        sorted_commentaries = sorted(commentaries, key=lambda c: c.start_time)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            
            for i, commentary in enumerate(sorted_commentaries, 1):
                start_time_vtt = self._seconds_to_vtt_time(commentary.start_time)
                end_time_vtt = self._seconds_to_vtt_time(commentary.end_time)
                
                # Format text for VTT (no HTML tags)
                text = commentary.text.strip()
                if commentary.reaction and commentary.reaction.strip() != text:
                    text += f" - {commentary.reaction.strip()}"
                
                f.write(f"{i}\n")
                f.write(f"{start_time_vtt} --> {end_time_vtt}\n")
                f.write(f"{text}\n\n")
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """Convert seconds to WebVTT time format (MM:SS.mmm)"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:06.3f}"
    
    def _generate_text_transcript(self, commentaries: List[Commentary], output_path: str):
        """Generate simple text transcript"""
        sorted_commentaries = sorted(commentaries, key=lambda c: c.start_time)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("HORSE RACING COMMENTARY TRANSCRIPT\n")
            f.write("=" * 50 + "\n\n")
            
            for commentary in sorted_commentaries:
                timestamp = self._seconds_to_readable_time(commentary.start_time)
                f.write(f"[{timestamp}] {commentary.text}")
                
                if commentary.reaction and commentary.reaction.strip() != commentary.text.strip():
                    f.write(f" - {commentary.reaction}")
                
                if commentary.replay_suggested:
                    f.write(" [REPLAY SUGGESTED]")
                
                f.write(f"\n")
    
    def _seconds_to_readable_time(self, seconds: float) -> str:
        """Convert seconds to readable time format (MM:SS)"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def validate_srt_file(self, srt_path: str) -> bool:
        """
        Validate SRT file format
        
        Args:
            srt_path: Path to SRT file
            
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(srt_path):
            print(f"SRT file not found: {srt_path}")
            return False
        
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic validation - check for sequence numbers and time format
            lines = content.strip().split('\n')
            
            i = 0
            entry_count = 0
            
            while i < len(lines):
                # Skip empty lines
                if not lines[i].strip():
                    i += 1
                    continue
                
                # Check sequence number
                if not lines[i].strip().isdigit():
                    print(f"Invalid sequence number at line {i+1}: {lines[i]}")
                    return False
                
                i += 1
                if i >= len(lines):
                    break
                
                # Check time format
                if " --> " not in lines[i]:
                    print(f"Invalid time format at line {i+1}: {lines[i]}")
                    return False
                
                i += 1
                entry_count += 1
                
                # Skip text lines until next entry or end
                while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
                    i += 1
            
            print(f"SRT file validation passed: {entry_count} entries found")
            return True
            
        except Exception as e:
            print(f"Error validating SRT file: {str(e)}")
            return False


if __name__ == "__main__":
    # Test SRT generator
    from src.commentary_generator import Commentary
    
    # Create sample commentaries
    sample_commentaries = [
        Commentary(
            text="Cuộc đua bắt đầu! Tất cả các ngựa xuất phát đồng loạt từ cổng.",
            reaction="Bắt đầu!",
            start_time=0.0,
            end_time=3.0,
            persona="kinh_tinh",
            confidence=0.9,
            event_type="starting_gate",
            replay_suggested=False
        ),
        Commentary(
            text="Lightning Bolt đang dẫn đầu với tốc độ ấn tượng!",
            reaction="Xuất sắc!",
            start_time=15.0,
            end_time=18.0,
            persona="chuyen_gia",
            confidence=0.85,
            event_type="acceleration",
            replay_suggested=False
        ),
        Commentary(
            text="Thunder Strike vượt qua Wind Runner ở khúc cua!",
            reaction="Tuyệt vời!",
            start_time=45.0,
            end_time=48.0,
            persona="kinh_tinh",
            confidence=0.8,
            event_type="overtaking",
            replay_suggested=True
        )
    ]
    
    # Test SRT generation
    generator = SRTGenerator()
    output_path = "test_output/commentary.srt"
    
    generator.generate_srt_from_commentaries(sample_commentaries, output_path)
    
    # Test validation
    is_valid = generator.validate_srt_file(output_path)
    print(f"SRT file valid: {is_valid}")
    
    # Test multi-format generation
    generator.generate_multi_format_subtitles(sample_commentaries, "test_output/commentary")
