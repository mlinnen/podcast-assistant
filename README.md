# Podcast Assistant: Audio Transcriber CLI

A powerful CLI tool that uses Google's Gemini Multimodal models to transcribe audio files. It features speaker diarization, emotion detection, language identification, and conversation marketing publication.

## Features

- **Multimodal Transcription**: Uses Gemini 1.5/2.0/3.0 Flash models for high-accuracy audio processing.
- **Speaker Diarization**: Identifies and labels multiple speakers (e.g., Speaker 1, Speaker 2).
- **Emotion Detection**:
  - **Inline**: Detects emotions for specific speech segments.
  - **Primary**: Identifies the dominant emotion of each segment.
- **Language Detection**: Identifies the spoken language (e.g., `en-US`).
- **Summarization**: Generates a concise summary of the entire conversation.
- **Marketing Content**: Generates optimized YouTube titles, descriptions (with line breaks), and Facebook posts.
- **YouTube Publishing**: Automatically publish generated videos to YouTube with SEO-optimized metadata.
- **Video Creation**: Creates an MP4 video by looping an image over the audio.
- **Transcript Review**: Exports a formatted Markdown document (`_review.md`) for easy proofreading.
- **Metadata**: Extracts file metadata (size, dates, duration).

## Prerequisites

- **Python 3.8+**
- **FFMpeg**: Required for video creation. Must be installed and available in your system PATH.
- **Google API Key**: Get one from [Google AI Studio](https://aistudio.google.com/) for Gemini access.
- **YouTube Data API v3**: Enable this in the [Google Cloud Console](https://console.cloud.google.com/) and download `client_secrets.json` to the project root for publishing.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mlinnen/podcast-assistant.git
   cd podcast-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   Create a `.env` file in the root directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

4. **YouTube Publishing Setup (Optional)**:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable **YouTube Data API v3**.
   - Create **OAuth 2.0 Client IDs** (Desktop app).
   - Download the `client_secrets.json` file and place it in the project root.
   - Use `client_secrets.json.example` as a template if needed.

## Usage

### Basic Usage

Transcribe an audio file using default settings:

```bash
python main.py --file path/to/audio.wav
```

### Advanced Usage

Specify the expected number of speakers and a specific Gemini model:

```bash
python main.py --file path/to/audio.wav --speakers 2 --model gemini-3-flash-preview
```

Create a video file from the audio and an image:

```bash
python main.py --file path/to/audio.wav --video path/to/image.png
```

Transcribe, create a video, and publish to YouTube:

```bash
python main.py --file path/to/audio.wav --video path/to/image.png --publish
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--file` | Path to the audio file (Required) | - |
| `--speakers` | Expected number of speakers | `2` |
| `--model` | Gemini model version to use | `gemini-3-flash-preview` |
| `--video` | Path to an image file to create a video from the audio | - |
| `--publish` | Publish the generated video to YouTube (requires setup) | `False` |
| `--api-key` | Google API Key (can also set via `GOOGLE_API_KEY` env var) | - |

## Utility Scripts

### List Available Models

You can list all Gemini models available to your API key by running:

```bash
python scripts/list_models.py
```

## Output

The tool creates an `out` directory containing a folder named after the audio file for each run. Existing files in the folder are overwritten on subsequent runs.

**Structure:**
```
out/
  sample_audio/
    sample_audio.wav       # Copy of the original file
    sample_audio.json      # Full transcription results and marketing content
    sample_audio_review.md # Formatted review document
    sample_audio.mp4       # Generated video (if --video is used)
```

**JSON Output Example:**
```json
{
  "FileName": "sample.wav",
  "LengthOfAudio": "00:05:30",
  "Speakers": ["Speaker 1", "Speaker 2"],
  "Dialog": [...],
  "Summary": "Hosts discuss the new podcast format...",
  "Publications": {
    "YouTube": {
      "Title": "Catchy Title",
      "Description": "Compelling summary\n\nURLs:\n- example.com"
    },
    "Facebook": {
      "Post": "Check out our latest episode!"
    },
    "Review": {
      "TranscriptFile": "sample_review.md"
    },
    "Video": {
      "VideoFile": "sample.mp4",
      "YouTubeVideoID": "dQw4w9WgXcQ"
    }
  }
}
```

## License

MIT
