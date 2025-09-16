"""
Event Detection Module for Horse Racing Commentary System
Uses Qwen2.5-VL to detect racing events from video clips
"""

import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import sys

# Add the parent directory to Python path to import qwen2.5vl
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qwen2_5vl import Qwen25VLGenerator


@dataclass
class RaceEvent:
    """Represents a detected racing event"""
    event_type: str        # overtaking, acceleration, collision, finish_line_cross, etc.
    start_time: float      # start timestamp in seconds
    end_time: float        # end timestamp in seconds
    confidence: float      # confidence score 0-1
    description: str       # detailed description
    horses_involved: List[str]  # list of horse IDs/numbers involved
    clip_id: str          # source clip identifier
    replay_suggested: bool # whether this event should be replayed


class EventDetector:
    """Detects racing events using Qwen2.5-VL vision model"""
    
    def __init__(self, model_path: str = "models/qwen2.5-vl-7b-instruct"):
        """
        Initialize event detector with Qwen2.5-VL model
        
        Args:
            model_path: Path to Qwen2.5-VL model
        """
        self.model = Qwen25VLGenerator(model_path=model_path)
        self.event_types = [
            "overtaking", "acceleration", "collision", "fall", 
            "finish_line_cross", "close_racing", "breakaway", 
            "starting_gate", "jockey_movement"
        ]
    
    def detect_events_from_clip(self, clip_path: str, start_time: float, end_time: float, clip_id: str) -> List[RaceEvent]:
        """
        Detect racing events from a single video clip
        
        Args:
            clip_path: Path to video clip file
            start_time: Start time of clip in original video
            end_time: End time of clip in original video
            clip_id: Unique identifier for this clip
            
        Returns:
            List of detected RaceEvent objects
        """
        if not os.path.exists(clip_path):
            print(f"Warning: Clip file not found: {clip_path}")
            return []
        
        # Create specialized prompt for event detection
        prompt = self._create_event_detection_prompt()
        
        try:
            # Use Qwen2.5-VL to analyze the video clip
            response = self.model.generate_script(clip_path, prompt, max_new_tokens=1000)
            
            # Parse the response to extract structured events
            events = self._parse_event_response(response, start_time, end_time, clip_id)
            
            return events
            
        except Exception as e:
            print(f"Error detecting events in clip {clip_id}: {str(e)}")
            return []
    
    def _create_event_detection_prompt(self) -> str:
        """Create specialized prompt for racing event detection"""
        return """Bạn là chuyên gia phân tích đua ngựa. Hãy phân tích video clip này và phát hiện các sự kiện quan trọng.

Các loại sự kiện cần phát hiện:
- overtaking: ngựa vượt qua ngựa khác
- acceleration: ngựa tăng tốc đột ngột
- collision: va chạm giữa các ngựa
- fall: ngựa hoặc jockey bị ngã
- finish_line_cross: ngựa về đích
- close_racing: nhiều ngựa chạy sát nhau
- breakaway: ngựa bứt phá khỏi nhóm
- starting_gate: bắt đầu cuộc đua
- jockey_movement: động tác đặc biệt của jockey

Hãy trả lời theo định dạng JSON sau:
{
  "events": [
    {
      "event_type": "tên sự kiện",
      "confidence": 0.8,
      "description": "mô tả chi tiết sự kiện",
      "horses_involved": ["số áo ngựa nếu nhìn thấy"],
      "replay_suggested": true/false
    }
  ]
}

Chỉ báo cáo những sự kiện bạn thực sự thấy trong video với confidence >= 0.6."""
    
    def _parse_event_response(self, response: str, start_time: float, end_time: float, clip_id: str) -> List[RaceEvent]:
        """Parse LLM response into structured RaceEvent objects"""
        events = []
        
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                if 'events' in data:
                    for event_data in data['events']:
                        # Validate required fields
                        if not all(key in event_data for key in ['event_type', 'confidence', 'description']):
                            continue
                            
                        # Filter by confidence threshold
                        if event_data['confidence'] < 0.6:
                            continue
                        
                        event = RaceEvent(
                            event_type=event_data['event_type'],
                            start_time=start_time,
                            end_time=end_time,
                            confidence=event_data['confidence'],
                            description=event_data['description'],
                            horses_involved=event_data.get('horses_involved', []),
                            clip_id=clip_id,
                            replay_suggested=event_data.get('replay_suggested', False)
                        )
                        events.append(event)
                        
        except json.JSONDecodeError:
            # Fallback: try to extract information from text response
            events = self._extract_events_from_text(response, start_time, end_time, clip_id)
        except Exception as e:
            print(f"Error parsing event response: {str(e)}")
            
        return events
    
    def _extract_events_from_text(self, response: str, start_time: float, end_time: float, clip_id: str) -> List[RaceEvent]:
        """Fallback method to extract events from unstructured text"""
        events = []
        
        # Simple keyword-based detection as fallback
        response_lower = response.lower()
        
        event_keywords = {
            'overtaking': ['vượt', 'vượt qua', 'overtaking', 'vượt lên'],
            'acceleration': ['tăng tốc', 'bứt tốc', 'acceleration', 'tăng speed'],
            'close_racing': ['sát nhau', 'cùng nhau', 'close', 'kịch tính'],
            'collision': ['va chạm', 'collision', 'đụng'],
            'fall': ['ngã', 'fall', 'té']
        }
        
        for event_type, keywords in event_keywords.items():
            for keyword in keywords:
                if keyword in response_lower:
                    event = RaceEvent(
                        event_type=event_type,
                        start_time=start_time,
                        end_time=end_time,
                        confidence=0.7,  # moderate confidence for keyword detection
                        description=f"Phát hiện {event_type} dựa trên phân tích văn bản",
                        horses_involved=[],
                        clip_id=clip_id,
                        replay_suggested=event_type in ['overtaking', 'collision', 'fall']
                    )
                    events.append(event)
                    break  # only add one event per type per clip
                    
        return events
    
    def analyze_video_clips(self, clips: List) -> List[RaceEvent]:
        """
        Analyze a list of video clips and detect all events
        
        Args:
            clips: List of VideoClip objects from video_processor
            
        Returns:
            List of all detected RaceEvent objects
        """
        all_events = []
        
        print(f"Analyzing {len(clips)} video clips for racing events...")
        
        for i, clip in enumerate(clips):
            print(f"Processing clip {i+1}/{len(clips)}: {clip.clip_id}")
            
            events = self.detect_events_from_clip(
                clip.clip_path, 
                clip.start_time, 
                clip.end_time, 
                clip.clip_id
            )
            
            all_events.extend(events)
            print(f"  Found {len(events)} events")
        
        print(f"Total events detected: {len(all_events)}")
        return all_events
    
    def save_events_to_json(self, events: List[RaceEvent], output_path: str):
        """Save detected events to JSON file"""
        events_data = [asdict(event) for event in events]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(events)} events to {output_path}")
    
    def load_events_from_json(self, input_path: str) -> List[RaceEvent]:
        """Load events from JSON file"""
        if not os.path.exists(input_path):
            return []
            
        with open(input_path, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        
        events = [RaceEvent(**event_data) for event_data in events_data]
        return events


if __name__ == "__main__":
    # Test the event detector
    detector = EventDetector()
    
    # Example usage with a test clip (if available)
    test_clip_path = "/home/quangnh58/horce_racing/test_output/clips/clip_0000_0.0_3.0.mp4"
    
    if os.path.exists(test_clip_path):
        events = detector.detect_events_from_clip(test_clip_path, 0.0, 3.0, "test_clip")
        print(f"Detected {len(events)} events:")
        for event in events:
            print(f"  - {event.event_type}: {event.description} (confidence: {event.confidence})")
    else:
        print(f"Test clip not found at {test_clip_path}")
        print("Please run video_processor.py first to generate test clips")
