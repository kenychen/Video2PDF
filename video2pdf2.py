import sys
import os
import argparse
from download_video import download_video
from translate_srt import translate_srt_file
from video_to_images import video_to_images
from convert_png_to_pdf import convert_png_to_pdf
import platform
import subprocess


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

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process video and subtitles.")
    parser.add_argument('video_name', help="Name of the video file to process.")
    #parser.add_argument('--embed', action='store_true', help="Use embedded subtitles.")

    # Parse arguments
    args = parser.parse_args()

    # Determine base name
    base_name = os.path.splitext(args.video_name)[0]
    #base_name = args.video_name

    ## Process video subs and create screenshots
    #if args.embed:
    #    process_video_subs(args.video_name) # with pre-embedd-sub
    #else:
    #    video_to_images(args.video_name) # without pre-embedd-sub    

    # 擷取影片和字幕檔案
    # Call the generate_srt function
    generate_srt(args.video_name)

    # 將影片轉換為圖片
    video_to_images(args.video_name)

    # 轉換圖片為PDF
    convert_png_to_pdf(base_name, base_name)

    # 開啟PDF
    #mac
    #os.system(f"open '{base_name}.pdf'")
    #os.system(f"start '{base_name}.pdf'")
    if platform.system() == "Windows":
        os.startfile(f"{base_name}.pdf")
    elif platform.system() == "Darwin":
        os.system(f"open '{base_name}.pdf'")
    else:
        print("不支援的操作系統")


