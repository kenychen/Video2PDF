import subprocess
import os

def download_video(url):
    video_format = "18"  # This will download mp4 video in 640x360 resolution
    output_template = "%(title)s.%(ext)s"  # This will name the video file as "title.mp4"

    # Build the yt-dlp command
    command = [
        "yt-dlp",
        "-f", video_format,
        "-o", output_template,
        url,
    ]

    # Execute the yt-dlp command
    # print(f"Executing command: {command}")
    subprocess.run(command, check=True)

    # Get the video title
    video_title = subprocess.check_output(["yt-dlp.exe", "--get-filename", "-o", "%(title)s", url])
    
    try:
        video_title = video_title.decode('utf-8')
    except UnicodeDecodeError:
        try:
            video_title = video_title.decode('big5', errors='ignore')
        except:
            print("無法解碼字串")
    #video_title = video_title.decode("utf-8").strip()
    video_title = video_title.replace('\n', '')
    video_filename = f"{video_title}.mp4"    
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #print("腳本所在的目錄:", script_dir)
    video_filename = os.path.join(script_dir, video_filename)
    #print(video_filename)

    # Call the generate_srt function
    generate_srt(video_filename)

    return video_filename

#改用whisper來產字幕
def generate_srt(video_filename):
    # Generate srt using whisper-ctranslate2
    #command_srt = [
    #    "whisper-ctranslate2",
    #    "--threads", "8",
    #    "--output_format", "srt",
    #    video_filename,
    #]
    command_srt = [
        "asr2.bat",        
        video_filename,
    ]

    # Execute the whisper-ctranslate2 command
    subprocess.run(command_srt, check=True)
