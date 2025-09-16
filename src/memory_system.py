"""
Memory System for Horse Racing Commentary
Manages short-term and long-term memory for race context
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class HorseProfile:
    """Profile information for a horse"""
    horse_id: str
    name: str
    number: str  # bib number
    jockey: str
    silks_color: str  # color description
    historical_wins: int
    preferred_distance: str
    last_5_races_stats: List[Dict]
    current_position: Optional[int] = None
    current_speed: Optional[float] = None


@dataclass
class RaceState:
    """Current state of the race"""
    race_id: str
    current_time: float
    leading_horse: str
    positions: Dict[str, int]  # horse_id -> position
    distances: Dict[str, float]  # horse_id -> distance from leader
    lap_times: Dict[str, List[float]]  # horse_id -> list of lap times


@dataclass
class ShortTermMemory:
    """Ephemeral memory for recent events and context"""
    recent_events: List[Dict]  # last N events
    current_positions: Dict[str, int]
    last_comment_timestamp: float
    race_phase: str  # start, middle, final_stretch, finish
    excitement_level: str  # low, medium, high
    last_mentioned_horses: List[str]


class MemorySystem:
    """Manages both short-term and long-term memory for racing commentary"""
    
    def __init__(self, memory_dir: str = "memory"):
        """
        Initialize memory system
        
        Args:
            memory_dir: Directory to store persistent memory files
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Short-term memory (in-memory, expires after race)
        self.short_term = ShortTermMemory(
            recent_events=[],
            current_positions={},
            last_comment_timestamp=0.0,
            race_phase="start",
            excitement_level="medium",
            last_mentioned_horses=[]
        )
        
        # Long-term memory (persistent)
        self.horse_profiles: Dict[str, HorseProfile] = {}
        self.race_history: Dict[str, RaceState] = {}
        
        # Load existing memory
        self._load_persistent_memory()
    
    def update_short_term_memory(self, events: List[Dict], current_time: float):
        """
        Update short-term memory with new events
        
        Args:
            events: List of new race events
            current_time: Current timestamp
        """
        # Add new events, keep only last 10
        self.short_term.recent_events.extend(events)
        self.short_term.recent_events = self.short_term.recent_events[-10:]
        
        # Update excitement level based on event types
        excitement_events = ['overtaking', 'collision', 'close_racing', 'finish_line_cross']
        if any(event.get('event_type') in excitement_events for event in events):
            self.short_term.excitement_level = "high"
        elif len(events) > 0:
            self.short_term.excitement_level = "medium"
        else:
            self.short_term.excitement_level = "low"
        
        # Update race phase based on time
        self._update_race_phase(current_time)
    
    def _update_race_phase(self, current_time: float):
        """Update race phase based on current time"""
        # Simple heuristic - can be made more sophisticated
        if current_time < 30:
            self.short_term.race_phase = "start"
        elif current_time < 120:
            self.short_term.race_phase = "middle"
        elif current_time < 180:
            self.short_term.race_phase = "final_stretch"
        else:
            self.short_term.race_phase = "finish"
    
    def get_context_for_commentary(self, current_time: float) -> Dict[str, Any]:
        """
        Get relevant context for commentary generation
        
        Args:
            current_time: Current timestamp in race
            
        Returns:
            Dictionary with memory context for LLM
        """
        context = {
            "short_term_memory": {
                "recent_events": self.short_term.recent_events[-5:],  # last 5 events
                "race_phase": self.short_term.race_phase,
                "excitement_level": self.short_term.excitement_level,
                "last_mentioned_horses": self.short_term.last_mentioned_horses[-3:],
                "time_since_last_comment": current_time - self.short_term.last_comment_timestamp
            },
            "long_term_memory": {
                "horse_profiles": {k: asdict(v) for k, v in self.horse_profiles.items()},
                "notable_patterns": self._get_notable_patterns()
            },
            "current_time": current_time
        }
        
        return context
    
    def _get_notable_patterns(self) -> List[str]:
        """Extract notable patterns from race history"""
        patterns = []
        
        # Analyze horse performance patterns
        for horse_id, profile in self.horse_profiles.items():
            if profile.historical_wins > 5:
                patterns.append(f"{profile.name} có lịch sử chiến thắng ấn tượng với {profile.historical_wins} lần thắng")
            
            if profile.preferred_distance:
                patterns.append(f"{profile.name} thường thể hiện tốt ở cự ly {profile.preferred_distance}")
        
        return patterns
    
    def update_horse_profile(self, horse_id: str, **kwargs):
        """Update horse profile information"""
        if horse_id not in self.horse_profiles:
            self.horse_profiles[horse_id] = HorseProfile(
                horse_id=horse_id,
                name=kwargs.get('name', f'Horse_{horse_id}'),
                number=kwargs.get('number', horse_id),
                jockey=kwargs.get('jockey', 'Unknown'),
                silks_color=kwargs.get('silks_color', 'Unknown'),
                historical_wins=kwargs.get('historical_wins', 0),
                preferred_distance=kwargs.get('preferred_distance', ''),
                last_5_races_stats=kwargs.get('last_5_races_stats', [])
            )
        else:
            # Update existing profile
            profile = self.horse_profiles[horse_id]
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
    
    def should_avoid_repetition(self, event_type: str, horses_involved: List[str]) -> bool:
        """
        Check if we should avoid repeating similar commentary
        
        Args:
            event_type: Type of event to comment on
            horses_involved: Horses involved in the event
            
        Returns:
            True if we should avoid commenting to prevent repetition
        """
        # Check recent events for similar commentary
        recent_event_types = [event.get('event_type') for event in self.short_term.recent_events[-3:]]
        
        # Avoid repeating same event type too frequently
        if recent_event_types.count(event_type) >= 2:
            return True
        
        # Avoid mentioning same horses too frequently
        mentioned_recently = set(self.short_term.last_mentioned_horses[-5:])
        horses_set = set(horses_involved)
        
        if len(horses_set.intersection(mentioned_recently)) == len(horses_set) and len(horses_set) > 0:
            return True
        
        return False
    
    def mark_commentary_generated(self, timestamp: float, horses_mentioned: List[str]):
        """Mark that commentary was generated at this timestamp"""
        self.short_term.last_comment_timestamp = timestamp
        self.short_term.last_mentioned_horses.extend(horses_mentioned)
        # Keep only recent mentions
        self.short_term.last_mentioned_horses = self.short_term.last_mentioned_horses[-10:]
    
    def _load_persistent_memory(self):
        """Load persistent memory from files"""
        horse_profiles_file = self.memory_dir / "horse_profiles.json"
        if horse_profiles_file.exists():
            try:
                with open(horse_profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for horse_id, profile_data in data.items():
                        self.horse_profiles[horse_id] = HorseProfile(**profile_data)
            except Exception as e:
                print(f"Error loading horse profiles: {e}")
    
    def save_persistent_memory(self):
        """Save persistent memory to files"""
        # Save horse profiles
        horse_profiles_file = self.memory_dir / "horse_profiles.json"
        with open(horse_profiles_file, 'w', encoding='utf-8') as f:
            data = {k: asdict(v) for k, v in self.horse_profiles.items()}
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def reset_short_term_memory(self):
        """Reset short-term memory for new race"""
        self.short_term = ShortTermMemory(
            recent_events=[],
            current_positions={},
            last_comment_timestamp=0.0,
            race_phase="start",
            excitement_level="medium",
            last_mentioned_horses=[]
        )
    
    def add_sample_horse_data(self):
        """Add some sample horse data for testing"""
        sample_horses = [
            {
                'horse_id': '1', 'name': 'Lightning Bolt', 'number': '1',
                'jockey': 'Nguyễn Văn A', 'silks_color': 'đỏ trắng',
                'historical_wins': 8, 'preferred_distance': '1200m'
            },
            {
                'horse_id': '2', 'name': 'Thunder Strike', 'number': '2', 
                'jockey': 'Trần Thị B', 'silks_color': 'xanh vàng',
                'historical_wins': 5, 'preferred_distance': '1400m'
            },
            {
                'horse_id': '3', 'name': 'Wind Runner', 'number': '3',
                'jockey': 'Lê Văn C', 'silks_color': 'tím trắng', 
                'historical_wins': 12, 'preferred_distance': '1600m'
            }
        ]
        
        for horse_data in sample_horses:
            self.update_horse_profile(**horse_data)


if __name__ == "__main__":
    # Test memory system
    memory = MemorySystem()
    memory.add_sample_horse_data()
    
    # Test context generation
    sample_events = [
        {'event_type': 'overtaking', 'horses_involved': ['1', '2'], 'timestamp': 45.0}
    ]
    
    memory.update_short_term_memory(sample_events, 45.0)
    context = memory.get_context_for_commentary(45.0)
    
    print("Memory context generated:")
    print(json.dumps(context, ensure_ascii=False, indent=2))
    
    # Save memory
    memory.save_persistent_memory()
    print("Memory saved successfully")
