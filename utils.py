import datetime
import jaconv
import os
import re
import requests
import subprocess
import tqdm
import UnityPy

from PyCriCodecs import ACB, CPK, USM

KEY = 0x0013F11BC5510101

RESOURCE_PATH = {
    "asset_bundle": "https://v2static.nogifes.jp/resource/Android_2017_4_1f1/",
    "focus_movie": "https://v2static.nogifes.jp/resource/Movie/Focus/",
    "high_focus_movie": "https://v2static.nogifes.jp/resource/Movie/HighFocusMovie/",
    "reward_movie": "https://v2static.nogifes.jp/resource/Movie/Reward/",
    "live_bg": "https://v2static.nogifes.jp/resource/Movie/LiveBg/",
    "high_live_bg": "https://v2static.nogifes.jp/resource/Movie/HighLiveBg/",
    "other_movie": "https://v2static.nogifes.jp/resource/Movie/Other/",
    "high_other_movie": "https://v2static.nogifes.jp/resource/Movie/HighOtherMovie/",
}

DOWNLOAD_PATH = {
    "member_card": "/mnt/data/downloads/nogifes/member_card/",
    "member_standing": "/mnt/data/downloads/nogifes/member_standing/",
    "focus_movie": "/mnt/data/downloads/nogifes/focus_movie/",
    "high_focus_movie": "/mnt/data/downloads/nogifes/high_focus_movie/",
    "reward_focus_movie": "/mnt/data/downloads/nogifes/reward_focus_movie/",
    "live_bg": "/mnt/data/downloads/nogifes/live_bg/",
    "high_live_bg": "/mnt/data/downloads/nogifes/high_live_bg/",
    "other_movie": "/mnt/data/downloads/nogifes/other_movie/",
    "high_other_movie": "/mnt/data/downloads/nogifes/high_other_movie/",
    "reward_movie": "/mnt/data/downloads/nogifes/reward_movie/",
}

FILENAME_REPLACEMENTS = {
    ":": " -",
    "/": " & ",
    "|": " - ",
    '"': "",
    "<": "(",
    ">": ")",
    "＜": " (",
    "＞": ")",
}

TEMP_DIR = "temp"

def sanitize_filename(title: str) -> str:
    name = title
    for k, v in FILENAME_REPLACEMENTS.items():
        name = name.replace(k, v)

    name = re.sub(r'[\\*?]', "", name)
    name = name.strip().rstrip(". ")

    return name or "untitled"

def download(url: str, file_name: str) -> bool:
    # print(f"Downloading {file_name}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
    except requests.RequestException:
        print(f"{file_name} download failed!")
        return False

    total_size = int(response.headers.get("Content-Length", 0))
    try:
        os.makedirs(TEMP_DIR, exist_ok=True)
        with open(os.path.join(TEMP_DIR, file_name), "wb") as f, tqdm.tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=file_name.ljust(32),
        ) as progress:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress.update(len(chunk))
    except Exception as e:
        print(f"{file_name} write failed: {e}")
        return False

    return True

def extrack_cpk(file_path: str) -> bool:
    print(f"Extracting CPK {file_path}...")
    try:
        cpk = CPK(file_path)
        cpk.extract()
    except Exception as e:
        print(f"{file_path} extraction failed: {e}")
        return False

    return True

def extract_usm(file_path: str) -> bool:
    print(f"Extracting USM {file_path}...")
    try:
        usm = USM(file_path, KEY)
        usm.extract(TEMP_DIR)
    except Exception as e:
        print(f"{file_path} extraction failed: {e}")
        return False

    return True

def extract_acb(file_path: str) -> bool:
    print(f"Extracting ACB {file_path}...")
    try:
        acb = ACB(file_path)
        acb.extract(True, KEY, TEMP_DIR)
    except Exception as e:
        print(f"{file_path} extraction failed: {e}")
        return False

    return True

def extract_unity_assets(file_path: str) -> list[str]:
    file_list: list[str] = []

    env = UnityPy.load(file_path)
    for obj in env.objects:
        if obj.type.name == "Texture2D":
            data = obj.parse_as_object()
            dest = os.path.join(TEMP_DIR, data.m_Name)

            dest, _ = os.path.splitext(dest)
            dest = dest + ".png"

            img = data.image
            img.save(dest)

            file_list.append(dest)

    return file_list

def run_cmd(cmd: list[str], show_output: bool = True) -> str:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
    )
    assert process.stdout is not None

    output_lines = []
    for line in process.stdout:
        output_lines.append(line)
        if show_output:
            print(line, end="")

    process.wait()
    return "".join(output_lines)


def ffmpeg_has_libfdk_aac() -> bool:
    return "libfdk_aac" in run_cmd(["ffmpeg", "-encoders"], False)

def remux_video(video_path: str, audio_path: str, output_path: str) -> bool:
    print(f"Remuxing {video_path}, {audio_path}...")
    try:
        if not os.path.exists(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        audio_codec = "aac"
        if ffmpeg_has_libfdk_aac():
            audio_codec = "libfdk_aac"

        run_cmd([
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", audio_codec, "-b:a", "256k",
            output_path
        ], False)
    except Exception as e:
        print(f"{video_path} remux failed: {e}")
        return False

    return True

def write_complete(dir_path: str):
    with open(os.path.join(dir_path, ".complete"), "w") as f:
        f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")

def check_complete(dir_path: str) -> bool:
    return os.path.exists(os.path.join(dir_path, ".complete"))

def normalize_unicode(text: str) -> str:
    return jaconv.h2z(text, kana=True, ascii=False, digit=False)
