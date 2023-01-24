from moviepy.editor import AudioFileClip
import os

path = r"test.flv"  # 视频路径
my=AudioFileClip(path)
my.write_audiofile(path.split('.')[0] + ".mp3")

