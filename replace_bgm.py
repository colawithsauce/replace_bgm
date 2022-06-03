#!/usr/bin/env python3
import os
import sys
import random
import tempfile
import ffmpeg

from datetime import datetime, timedelta


class rule_entry:
    def __init__(self, url: str, duration: int):
        self.url = url
        self.duration = duration
        self.audio_list = []

    def print(self):
        print("{}: duration {}".format(self.url, self.duration))
        for i in self.audio_list:
            print("\t{}".format(i))

    def get(self):
        "得到一个随机的内容"
        return random.choice(self.audio_list)

    def fill_audio_list(self):
        things_in_dir = [os.path.join(self.url, f) for f in os.listdir(self.url)]
        files_indir = [
            f for f in things_in_dir if os.path.isfile(f) or os.path.islink(f)
        ]
        self.audio_list = files_indir


class entry_list:
    entries: list = []
    total_time = 0
    cur_time = 0
    cur_index = 0

    def __init__(self):
        return

    def append(url: str, duration: int):
        entry = rule_entry(url, duration)
        entry.fill_audio_list()
        entry_list.entries.append(entry)

    def get_next():
        "获取规则限定下的下一首歌"
        e = entry_list
        if e.cur_time < e.entries[e.cur_index].duration * 60:
            ret = e.entries[e.cur_index].get()
            e.cur_time += get_duration(ret)
        else:
            e.cur_time = 0
            e.cur_index = (e.cur_index + 1) % len(e.entries)
            return e.get_next()

        e.total_time += get_duration(ret)
        return ret


# (开始，结束，曲名)
timestamp_songname = []  # 什么时候播放了什么歌，一个 pair 的列表


def get_rule(script):
    "获取script文件对应的规则类"
    # 一行行读取分析
    with open(script) as f:
        script_str = [line.rstrip() for line in f]
        script_str = [line for line in script_str if len(line) != 0 and line[0] != "#"]
        for name, duration in zip(*[iter(script_str)] * 2):
            name = os.path.abspath(name)
            entry_list.append(name, int(duration))
            print(name, duration)


def get_duration(url):
    "获取多媒体文件的时长（seconds）"
    return float(ffmpeg.probe(url)["format"]["duration"])


def get_song_name(url):
    "获取多媒体文件的歌曲名"
    try:
        title = ffmpeg.probe(url)["format"]["tags"]["title"]
        author = ffmpeg.probe(url)["format"]["tags"]["artist"]
        song_name = "{} - {}".format(title, author)
    except BaseException:
        song_name = os.path.basename(url)

    song_name = song_name.replace("<", "(").replace(">", ")")
    return song_name


def generate_audio_playlist(duration):
    "根据规则生成一段长度比 duration 稍微长一点的播放列表，并且将时间-曲名的对应关系存储下来。"
    rst = []
    while entry_list.total_time < duration * 60:
        prev_timestamp = entry_list.total_time
        item = entry_list.get_next()
        rst.append("file '{}'".format(item))  # 添加清单项

        # (开始，结束，曲名)
        timestamp_songname.append(
            (
                datetime.utcfromtimestamp(prev_timestamp),
                datetime.utcfromtimestamp(entry_list.total_time),
                get_song_name(item),
            )
        )

    return rst


def get_srt_string():
    "从全局的 timestamp 文件获取歌词文件"
    ret = ""
    for i, item in enumerate(timestamp_songname):
        display_duration = timedelta(seconds=20)  # 字幕只显示 20 秒钟的时间
        start = item[0]
        end = start + display_duration
        ret += "{index}\n{start} --> {end}\n{text}\n\n".format(
            index=i,
            start=start.strftime("%H:%M:%S.%f")[:-2],
            end=end.strftime("%H:%M:%S.%f")[:-2],
            text=item[2],
        )
    return ret


def merge_it(playlist: str, video: str, output: str):
    "根据 playlist 指向的文件，替换 video 的音轨，输出为 output，并加上字幕"
    srt_string = get_srt_string()
    with tempfile.NamedTemporaryFile("w+") as subtitle:
        subtitle.write(srt_string)
        subtitle.flush()  # 写入文件（必不可少！）
        command = "ffmpeg -f concat -safe 0 -vn -i {audio}\
        -an -i {video}\
        -i {subtitle}\
        -c:a copy -c:v copy -y {output}".format(
            audio=playlist, video=video, output=output, subtitle=subtitle.name
        )
        print("executing: %s" % command)
        print(srt_string)
        os.system(command)
        subtitle.close()


if __name__ == "__main__":
    get_rule("./script.txt")
    playlist = generate_audio_playlist(100)
    with tempfile.NamedTemporaryFile("w+") as f:
        f.writelines([line + "\n" for line in playlist])
        f.flush()
        merge_it(f.name, sys.argv[1], sys.argv[2])
