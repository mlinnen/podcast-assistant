# Audio Transcriber CLI

A powerful CLI tool that uses Google's Gemini Multimodal models to transcribe audio files. It features speaker diarization, emotion detection, language identification, and conversation summarization.

## Features

- **Multimodal Transcription**: Uses Gemini 1.5/2.0/3.0 Flash models for high-accuracy audio processing.
- **Speaker Diarization**: Identifies and labels multiple speakers (e.g., Speaker 1, Speaker 2).
- **Emotion Detection**:
  - **Inline**: Detects emotions for specific speech segments.
  - **Primary**: Identifies the dominant emotion of each segment.
- **Language Detection**: Identifies the spoken language (e.g., `en-US`).
- **Summarization**: Generates a concise summary of the entire conversation.
- **Marketing Content**: Generates optimized YouTube titles, descriptions (with line breaks), and Facebook posts.
- **Transcript Review**: Exports a formatted Markdown document (`_review.md`) for easy proofreading.
- **Metadata**: Extracts file metadata (size, dates, duration).

## Prerequisites

- **Python 3.8+**
- **Google API Key**: Get one from [Google AI Studio](https://aistudio.google.com/).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/podcast-assistant.git
   cd podcast-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

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

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--file` | Path to the audio file (Required) | - |
| `--speakers` | Expected number of speakers | `2` |
| `--model` | Gemini model version to use | `gemini-3-flash-preview` |
| `--api-key` | Google API Key (can also set via `GOOGLE_API_KEY` env var) | - |

## Output

The tool creates an `out` directory containing a folder named after the audio file for each run. Existing files in the folder are overwritten on subsequent runs.

**Structure:**
```
out/
  sample_audio/
    sample_audio.wav       # Copy of the original file
    sample_audio.json      # Full transcription results and marketing content
    sample_audio_review.md # Formatted review document
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
    }
  }
}
```

## License

[MIT](LICENSE)
