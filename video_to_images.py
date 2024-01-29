import os
from moviepy.editor import TextClip, ImageClip, CompositeVideoClip, VideoFileClip
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import subprocess
import json
import textwrap

def get_video_dimensions(video_path):

    # 处理 16:9
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=width,height,sample_aspect_ratio", "-of", "json", video_path]
    output = subprocess.check_output(cmd).decode("utf-8")
    dimensions = json.loads(output)["streams"][0]

    width = dimensions["width"]
    height = dimensions["height"]
    sar = dimensions.get("sample_aspect_ratio", "1:1").split(":")
    sar = float(sar[0]) / float(sar[1])

    # Calculate display width based on sample aspect ratio
    display_width = int(width * sar)

    return display_width, height



def wrap_text(text, max_width, font, font_size):
    text_clip = TextClip("T", font=font, fontsize=font_size)  # 用於計算字體尺寸
    max_chars_per_line = max_width // (text_clip.size[0] * 2)  # 估算每行最大字符數
    wrapped_text = textwrap.wrap(text, width=max_chars_per_line)
    return "\n".join(wrapped_text)


def adjust_text(text, max_length, text_size, max_width):
    if len(text) > max_length:
        text_size -= 5
        wrapped_text = textwrap.wrap(text, width=int(max_width / text_size * 1.8))
        return "\n".join(wrapped_text), text_size
    return text, text_size



def adjust_font_size(text, max_length, initial_size, scale_factor, max_width):
    text_size = initial_size
    while len(text) > max_length and text_size > 10:
        text_size -= 1  # 適當減少字體大小
        if len(text) * text_size * scale_factor <= max_width:
            break  # 如果字體大小適合，則停止調整
    return text_size

def process_subtitle(args):
    i, subtitle, video_file_name, base_name = args
    clip = VideoFileClip(video_file_name)

    parts = subtitle.split("\n")
    if len(parts) < 3 or " --> " not in parts[1]:
        return None  # 跳過格式不正確的字幕

    time_line = parts[1]
    times = time_line.split(" --> ")
    start_time = times[0].split(":")
    end_time = times[1].split(":")
    start_time = int(start_time[0]) * 3600 + int(start_time[1]) * 60 + float(start_time[2].replace(",", "."))
    end_time = int(end_time[0]) * 3600 + int(end_time[1]) * 60 + float(end_time[2].replace(",", "."))
    mid_time = start_time + ((end_time - start_time) / 3)

    frame_width, frame_height = get_video_dimensions(video_file_name)
    scale_factor = frame_width / 1920 if frame_width > frame_height else frame_height / 1920
    max_width = frame_width - 40  # 最大字幕寬度

    font = "C:\\\\Windows\\\\Fonts\\\\kaiu.ttf"
    color = 'yellow'
    bg_color = 'black'
    stroke_width = 0.25 * scale_factor
    max_width = frame_width - 40  # 最大字幕寬度

    text_clips = []
    if len(parts) >= 4:  # 雙語字幕
        # 處理第一種語言（英文）
        initial_size = 50 * scale_factor
        text_size_first = adjust_font_size(parts[2], 75, initial_size, scale_factor, max_width)
        wrapped_text_first = wrap_text(parts[2], max_width, font, text_size_first)
        text_pos_first = ('center', frame_height - 150)

        text_clip_first = (TextClip(wrapped_text_first, font=font, fontsize=text_size_first, color=color, bg_color=bg_color, stroke_width=stroke_width)
                           .set_duration(end_time - mid_time)
                           .set_position(text_pos_first))
        text_clips.append(text_clip_first)

        # 處理第二種語言（中文）
        text_size_second = adjust_font_size(parts[3], 30, initial_size, scale_factor, max_width)
        wrapped_text_second = wrap_text(parts[3], max_width, font, text_size_second)
        text_pos_second = ('center', frame_height - 70)

        text_clip_second = (TextClip(wrapped_text_second, font=font, fontsize=text_size_second, color=color, bg_color=bg_color, stroke_width=stroke_width)
                            .set_duration(end_time - mid_time)
                            .set_position(text_pos_second))
        text_clips.append(text_clip_second)
    else:  # 單語字幕
        text = parts[2]
        initial_size = 50 * scale_factor
        text_size = adjust_font_size(text, 75, initial_size, scale_factor, max_width)
        wrapped_text = wrap_text(text, max_width, font, text_size)
        text_pos = ('center', frame_height - 100)

        text_clip = (TextClip(wrapped_text, font=font, fontsize=text_size, color=color, bg_color=bg_color, stroke_width=stroke_width)
                     .set_duration(end_time - mid_time)
                     .set_position(text_pos))
        text_clips.append(text_clip)


    frame = clip.get_frame(mid_time)
    frame_clip = ImageClip(frame).set_duration(end_time - mid_time).resize((frame_width, frame_height))

    final = CompositeVideoClip([frame_clip, *text_clips])
    final.save_frame(f"{base_name}/{i:04}.png")

    return i





def video_to_images(video_file_name: str):
    base_name = video_file_name.rsplit('.', 1)[0]
    #zh_subtitle_file_name = base_name + '.zh.srt'
    zh_subtitle_file_name = base_name + '.srt'

    with open(zh_subtitle_file_name, "r",encoding="utf-8") as f:
        zh_subtitles = f.read().split("\n\n")

    # Create directory to store frames
    try:
        if not os.path.exists(base_name):
            os.makedirs(base_name)
    except OSError as e:
        print(f"Failed to create directory: {base_name}. Error: {e}")
        raise

    with Pool(cpu_count()) as pool:
        for _ in tqdm(pool.imap_unordered(process_subtitle, [(i, zh_subtitles[i], video_file_name, base_name) for i in range(len(zh_subtitles))]), total=len(zh_subtitles)):
            pass
