import os
import subprocess
import shutil

def create_video(audio_path, image_path, output_dir):
    """
    Creates an MP4 video from an audio file and an image file using ffmpeg.

    Args:
        audio_path (str): Path to the input audio file.
        image_path (str): Path to the input image file.
        output_dir (str): Directory where the output video will be saved.

    Returns:
        str: Path to the generated video file, or None if ffmpeg is not available or fails.
    """
    
    # Check if ffmpeg is available
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg is not installed or not in the system PATH.")
        return None

    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return None

    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None

    # Construct output filename
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_filename = f"{base_name}.mp4"
    output_path = os.path.join(output_dir, output_filename)

    print(f"Creating video from {audio_path} and {image_path}...")
    
    # Construct ffmpeg command
    # -loop 1: Loop the image
    # -i image_path: Input image
    # -i audio_path: Input audio
    # -c:v libx264: Video codec
    # -tune stillimage: Tune for still image
    # -c:a aac: Audio codec
    # -b:a 192k: Audio bitrate
    # -pix_fmt yuv420p: Pixel format for compatibility
    # -shortest: Finish encoding when the shortest input stream ends (the audio)
    # -y: Overwrite output file if it exists
    command = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-y",
        output_path
    ]

    try:
        # Run ffmpeg command
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Video created successfully at {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error creating video: {e}")
        # Print stderr for debugging if needed, but be careful with large output
        print(f"ffmpeg stderr: {e.stderr.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
