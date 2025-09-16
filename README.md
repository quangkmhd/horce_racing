# 🐎 Horse Racing Commentary Generator

AI-powered system that automatically generates live commentary for horse racing videos using computer vision and large language models.

## 🌟 Features

- **Video Processing**: Automatically segments MP4 videos into analyzable clips
- **Event Detection**: Uses Qwen2.5-VL vision model to detect racing events (overtaking, acceleration, collisions, etc.)
- **Smart Memory System**: Maintains short-term and long-term memory for contextual commentary
- **Multiple Personas**: Supports different commentary styles (dramatic, expert analysis, family-friendly, humorous)  
- **Multi-format Output**: Generates SRT, WebVTT, and text transcript files
- **Batch Processing**: Process multiple videos automatically

## 🏗️ Architecture

```
Video Input (MP4) 
    ↓
Video Processor (clips + frames)
    ↓  
Event Detection (Qwen2.5-VL)
    ↓
Memory System (context + history)
    ↓
Commentary Generation (Llama70B)
    ↓
SRT Output (subtitles)
```

## 🚀 Quick Start

### Prerequisites

1. **Qwen2.5-VL Model**: Download and place in `models/qwen2.5-vl-7b-instruct/`
2. **API Access**: Configure Llama70B API credentials in `.env`
3. **Python 3.8+**: Required for all dependencies

### Installation  

```bash
# Clone the repository
git clone <repository-url>
cd horce_racing

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API credentials
```

### Configuration

Create/edit `.env` file:
```bash
API_KEY=your-llama-api-key
BASE_URL=https://your-api-endpoint.com
MODEL=Llama-3.3-70B-Instruct
```

### Basic Usage

```bash
# Process a single video
python main.py process video.mp4

# Process with custom settings
python main.py process video.mp4 --output-dir my_output --clip-duration 2.0

# Process multiple videos
python main.py batch /path/to/videos/

# Get video information
python main.py info video.mp4
```

### Advanced Usage

```bash
# Custom model path
python main.py process video.mp4 --model-path /custom/path/to/qwen2.5vl

# Batch process with pattern
python main.py batch /videos/ --pattern "race_*.mp4"
```

## 📁 Project Structure

```
horce_racing/
├── main.py                 # Main CLI application
├── requirements.txt        # Python dependencies
├── .env                   # API configuration  
├── src/
│   ├── video_processor.py    # Video segmentation
│   ├── event_detector.py     # Racing event detection
│   ├── memory_system.py      # Context memory management
│   ├── commentary_generator.py # Commentary generation
│   └── srt_generator.py      # Subtitle file creation
├── models/                # AI models directory
├── output/               # Generated files
└── memory/              # Persistent memory storage
```

## 🎯 Event Detection

The system detects these racing events:

- **overtaking**: Horse passes another horse
- **acceleration**: Sudden speed increase  
- **collision**: Contact between horses
- **fall**: Horse or jockey falls
- **finish_line_cross**: Crossing the finish line
- **close_racing**: Multiple horses racing closely
- **breakaway**: Horse breaks away from pack
- **starting_gate**: Race start
- **jockey_movement**: Special jockey actions

## 🎭 Commentary Personas

- **Kịch tính (Dramatic)**: High energy, intense commentary
- **Chuyên gia (Expert)**: Technical analysis and insights  
- **Hài hước (Humorous)**: Light-hearted, entertaining style
- **An toàn (Family-friendly)**: Safe, inclusive commentary

## 📄 Output Formats

The system generates multiple output formats:

- **SRT** (`.srt`): Standard subtitle format
- **WebVTT** (`.vtt`): Web video text tracks
- **Text Transcript** (`.txt`): Plain text commentary
- **Events JSON**: Detected events data
- **Commentary JSON**: Generated commentary data

## 🔧 Configuration Options

### Video Processing
- `clip_duration`: Duration of video clips (default: 3.0s)
- `output_dir`: Output directory (default: 'output')

### Event Detection  
- `model_path`: Path to Qwen2.5-VL model
- `confidence_threshold`: Minimum confidence for events (0.6)

### Commentary Generation
- Persona selection based on event type and race phase
- Memory-based repetition avoidance
- Multi-language support (Vietnamese focus)

## 🧠 Memory System

### Short-term Memory
- Recent events (last 10)
- Current race phase
- Excitement level
- Recently mentioned horses

### Long-term Memory
- Horse profiles and statistics
- Jockey information  
- Historical race data
- Performance patterns

## 🛠️ Development

### Running Tests

```bash
# Test individual modules
python src/video_processor.py
python src/event_detector.py
python src/memory_system.py

# Test complete pipeline
python main.py process test_video.mp4
```

### Adding New Features

1. **New Event Types**: Extend `event_types` in `EventDetector`
2. **New Personas**: Add to `personas` dict in `CommentaryGenerator`  
3. **Custom Memory Schema**: Modify `MemorySystem` classes
4. **Output Formats**: Extend `SRTGenerator` with new formats

## 📊 Performance

- **Video Processing**: ~1-2 clips per second
- **Event Detection**: ~2-3 seconds per clip (depends on model)
- **Commentary Generation**: ~1-2 seconds per event (API dependent)
- **Memory**: Minimal RAM usage, persistent storage

## 🐛 Troubleshooting

### Common Issues

1. **Model Loading Error**: Ensure Qwen2.5-VL model is properly downloaded
2. **API Connection**: Verify `.env` credentials and network connectivity
3. **Video Format**: Currently supports MP4, convert other formats first
4. **Memory Issues**: For long videos, consider shorter clip durations

### Debug Mode

Enable verbose logging by setting environment variable:
```bash
export DEBUG=1
python main.py process video.mp4
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Qwen2.5-VL**: Vision-language model for event detection
- **Llama**: Large language model for commentary generation
- **OpenCV**: Video processing capabilities
- **FPT Cloud**: API infrastructure

## 📞 Support

For questions or issues:
- Open GitHub issue
- Check troubleshooting section
- Review log files in output directory

---

**Note**: This system is designed for offline processing of horse racing videos. Real-time streaming capabilities would require additional optimization and infrastructure.