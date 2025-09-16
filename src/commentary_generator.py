"""
Commentary Generation Module for Horse Racing System
Uses Llama70B to generate racing commentary from structured events
"""

import json
import os
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llama70b import ChatBot
from src.event_detector import RaceEvent
from src.memory_system import MemorySystem


@dataclass
class Commentary:
    """Represents generated commentary for a racing moment"""
    text: str
    reaction: str
    start_time: float
    end_time: float
    persona: str
    confidence: float
    event_type: str
    replay_suggested: bool = False


class CommentaryGenerator:
    """Generates racing commentary using Llama70B based on detected events and memory"""
    
    def __init__(self):
        """Initialize commentary generator with Llama70B chatbot"""
        self.chatbot = ChatBot()
        self.memory_system = MemorySystem()
        
        # Load personas and styles
        self.personas = {
            "kinh_tinh": {
                "name": "Kịch tính",
                "style": "intense, dramatic, short sentences",
                "voice": "excited, high energy"
            },
            "chuyen_gia": {
                "name": "Chuyên gia phân tích", 
                "style": "analytical, technical, detailed",
                "voice": "professional, informative"
            },
            "hai_huoc": {
                "name": "Hài hước",
                "style": "light-hearted, playful wordplay",
                "voice": "entertaining, fun"
            },
            "an_toan": {
                "name": "An toàn gia đình",
                "style": "family-friendly, positive",
                "voice": "warm, inclusive"
            }
        }
    
    def generate_commentary_for_event(self, event: RaceEvent, memory_context: Dict) -> Optional[Commentary]:
        """
        Generate commentary for a single racing event
        
        Args:
            event: RaceEvent object with event details
            memory_context: Context from memory system
            
        Returns:
            Commentary object or None if should skip
        """
        # Check if we should avoid repetition
        if self.memory_system.should_avoid_repetition(event.event_type, event.horses_involved):
            return None
        
        # Select appropriate persona based on event type and race phase
        persona = self._select_persona(event, memory_context)
        
        # Create prompt for commentary generation
        prompt = self._create_commentary_prompt(event, memory_context, persona)
        
        try:
            # Generate commentary using Llama70B
            response = self.chatbot.send_message(prompt)
            
            # Parse response into structured commentary
            commentary = self._parse_commentary_response(response, event, persona)
            
            if commentary:
                # Update memory with generated commentary
                self.memory_system.mark_commentary_generated(
                    event.start_time, 
                    event.horses_involved
                )
            
            return commentary
            
        except Exception as e:
            print(f"Error generating commentary for event {event.clip_id}: {str(e)}")
            return None
    
    def _select_persona(self, event: RaceEvent, memory_context: Dict) -> str:
        """Select appropriate persona based on event and context"""
        excitement_level = memory_context.get('short_term_memory', {}).get('excitement_level', 'medium')
        race_phase = memory_context.get('short_term_memory', {}).get('race_phase', 'middle')
        
        # Dramatic events get kịch tính persona
        if event.event_type in ['collision', 'fall', 'finish_line_cross', 'overtaking']:
            return "kinh_tinh"
        
        # Technical events get chuyên gia persona
        elif event.event_type in ['acceleration', 'jockey_movement']:
            return "chuyen_gia"
        
        # Safe default based on race phase
        elif race_phase == "finish":
            return "kinh_tinh"
        else:
            return "an_toan"
    
    def _create_commentary_prompt(self, event: RaceEvent, memory_context: Dict, persona: str) -> str:
        """Create specialized prompt for commentary generation"""
        persona_info = self.personas[persona]
        
        # Build context string
        short_term = memory_context.get('short_term_memory', {})
        recent_events_summary = self._summarize_recent_events(short_term.get('recent_events', []))
        
        # Create horse information string
        horse_info = ""
        if event.horses_involved and memory_context.get('long_term_memory', {}).get('horse_profiles'):
            horse_profiles = memory_context['long_term_memory']['horse_profiles']
            for horse_id in event.horses_involved:
                if horse_id in horse_profiles:
                    profile = horse_profiles[horse_id]
                    horse_info += f"- {profile['name']} (#{profile['number']}): {profile['historical_wins']} chiến thắng, jockey {profile['jockey']}\n"
        
        prompt = f"""[Persona]: "{persona_info['name']}" (phong cách: {persona_info['style']})
[Bối cảnh cuộc đua]: Thời điểm = {event.start_time:.1f}s - {event.end_time:.1f}s
[Giai đoạn]: {short_term.get('race_phase', 'middle')}
[Mức độ kịch tính]: {short_term.get('excitement_level', 'medium')}

[Bộ nhớ ngắn hạn]: {recent_events_summary}

[Thông tin ngựa]:
{horse_info}

[Sự kiện hiện tại]: 
- Loại: {event.event_type}
- Mô tả: {event.description}
- Độ tin cậy: {event.confidence}
- Ngựa liên quan: {', '.join(event.horses_involved) if event.horses_involved else 'Không xác định'}

Nhiệm vụ: Viết script bình luận ngắn (25-35 từ) và 1 câu phản ứng ngắn (3-6 từ) cho khoảnh khắc này.

Quy tắc:
- Không lặp lại thông tin đã nói trong 15s trước
- Nếu độ tin cậy < 0.7, bắt đầu bằng "Có vẻ như..." hoặc "Dường như..."
- Sử dụng ngôn ngữ phù hợp với persona {persona_info['name']}
- Tập trung vào hành động đang diễn ra, không dài dòng về lịch sử

Định dạng trả lời (JSON):
{{
  "text": "script bình luận chính",
  "reaction": "câu phản ứng ngắn",
  "confidence": {event.confidence},
  "persona": "{persona}",
  "replay_suggested": {str(event.replay_suggested).lower()}
}}"""

        return prompt
    
    def _summarize_recent_events(self, recent_events: List[Dict]) -> str:
        """Summarize recent events for context"""
        if not recent_events:
            return "Chưa có sự kiện gần đây"
        
        summary_parts = []
        for event in recent_events[-3:]:  # last 3 events
            event_type = event.get('event_type', 'unknown')
            horses = event.get('horses_involved', [])
            horses_str = f" (ngựa {', '.join(horses)})" if horses else ""
            summary_parts.append(f"{event_type}{horses_str}")
        
        return "Sự kiện gần đây: " + ", ".join(summary_parts)
    
    def _parse_commentary_response(self, response: str, event: RaceEvent, persona: str) -> Optional[Commentary]:
        """Parse LLM response into Commentary object"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                # Validate required fields
                if 'text' in data and 'reaction' in data:
                    commentary = Commentary(
                        text=data['text'],
                        reaction=data['reaction'],
                        start_time=event.start_time,
                        end_time=event.end_time,
                        persona=persona,
                        confidence=data.get('confidence', event.confidence),
                        event_type=event.event_type,
                        replay_suggested=data.get('replay_suggested', event.replay_suggested)
                    )
                    return commentary
            
            # Fallback: extract text directly
            return self._extract_commentary_from_text(response, event, persona)
            
        except json.JSONDecodeError:
            return self._extract_commentary_from_text(response, event, persona)
        except Exception as e:
            print(f"Error parsing commentary response: {str(e)}")
            return None
    
    def _extract_commentary_from_text(self, response: str, event: RaceEvent, persona: str) -> Commentary:
        """Fallback method to extract commentary from unstructured text"""
        # Simple extraction - take first sentence as main text
        sentences = response.split('.')
        main_text = sentences[0].strip() if sentences else response.strip()
        
        # Generate simple reaction based on event type
        reactions = {
            'overtaking': 'Tuyệt vời!',
            'collision': 'Ôi không!',
            'acceleration': 'Nhanh quá!',
            'finish_line_cross': 'Về đích!',
            'fall': 'Nguy hiểm!',
            'close_racing': 'Kịch tính!'
        }
        
        reaction = reactions.get(event.event_type, 'Thú vị!')
        
        return Commentary(
            text=main_text[:150],  # limit text length
            reaction=reaction,
            start_time=event.start_time,
            end_time=event.end_time,
            persona=persona,
            confidence=0.7,  # moderate confidence for fallback
            event_type=event.event_type,
            replay_suggested=event.replay_suggested
        )
    
    def generate_commentary_for_events(self, events: List[RaceEvent]) -> List[Commentary]:
        """
        Generate commentary for a list of racing events
        
        Args:
            events: List of RaceEvent objects
            
        Returns:
            List of Commentary objects
        """
        commentaries = []
        
        print(f"Generating commentary for {len(events)} events...")
        
        for i, event in enumerate(events):
            print(f"Processing event {i+1}/{len(events)}: {event.event_type}")
            
            # Get memory context for this timestamp
            memory_context = self.memory_system.get_context_for_commentary(event.start_time)
            
            # Update memory with this event
            event_dict = {
                'event_type': event.event_type,
                'horses_involved': event.horses_involved,
                'timestamp': event.start_time,
                'confidence': event.confidence
            }
            self.memory_system.update_short_term_memory([event_dict], event.start_time)
            
            # Generate commentary
            commentary = self.generate_commentary_for_event(event, memory_context)
            
            if commentary:
                commentaries.append(commentary)
                print(f"  Generated: {commentary.text}")
            else:
                print(f"  Skipped (repetition avoidance)")
        
        print(f"Generated {len(commentaries)} commentaries from {len(events)} events")
        return commentaries
    
    def save_commentaries_to_json(self, commentaries: List[Commentary], output_path: str):
        """Save commentaries to JSON file"""
        data = [asdict(commentary) for commentary in commentaries]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(commentaries)} commentaries to {output_path}")


if __name__ == "__main__":
    # Test commentary generator
    generator = CommentaryGenerator()
    
    # Add sample horse data
    generator.memory_system.add_sample_horse_data()
    
    # Create sample event
    sample_event = RaceEvent(
        event_type="overtaking",
        start_time=45.0,
        end_time=48.0,
        confidence=0.85,
        description="Ngựa số 1 vượt qua ngựa số 2 ở khúc cua",
        horses_involved=["1", "2"],
        clip_id="test_clip",
        replay_suggested=True
    )
    
    # Test commentary generation
    memory_context = generator.memory_system.get_context_for_commentary(45.0)
    commentary = generator.generate_commentary_for_event(sample_event, memory_context)
    
    if commentary:
        print(f"Generated commentary: {commentary.text}")
        print(f"Reaction: {commentary.reaction}")
    else:
        print("No commentary generated")
