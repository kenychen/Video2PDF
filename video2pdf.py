import sys
from transcript import process_video_subs
from convert_png_to_pdf import convert_png_to_pdf
from video_to_images import video_to_images
import os
import argparse
import platform

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process video and subtitles.")
    parser.add_argument('video_name', help="Name of the video file to process.")
    parser.add_argument('--embed', action='store_true', help="Use embedded subtitles.")
    parser.add_argument('--noshow', action='store_true', help="Do not open the PDF file automatically.")

    # Parse arguments
    args = parser.parse_args()

    # Determine base name
    base_name = os.path.splitext(args.video_name)[0]

    # Process video subs and create screenshots
    if args.embed:
        process_video_subs(args.video_name) # with pre-embedd-sub
    else:
        video_to_images(args.video_name) # without pre-embedd-sub

    # Convert screenshots to PDF
    convert_png_to_pdf(base_name, base_name)

    #os.system(f"open '{base_name}.pdf'")
    # 開啟PDF
    #mac
    #os.system(f"open '{base_name}.pdf'")
    #os.system(f"start '{base_name}.pdf'")
    # Open PDF only if --noshow is not set
    if not args.noshow:
        if platform.system() == "Windows":
            os.startfile(f"{base_name}.pdf")
        elif platform.system() == "Darwin":
            os.system(f"open '{base_name}.pdf'")
        else:
            print("不支援的操作系統")


if __name__ == "__main__":
    main()
