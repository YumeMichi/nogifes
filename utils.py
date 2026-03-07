import datetime
import functools
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
    "asset_bundle": "https://v1static.nogifes.jp/resource/Android_2017_4_1f1/",
    "focus_movie": "https://v1static.nogifes.jp/resource/Movie/Focus/",
    "high_focus_movie": "https://v1static.nogifes.jp/resource/Movie/HighFocusMovie/",
    "reward_movie": "https://v1static.nogifes.jp/resource/Movie/Reward/",
    "live_bg": "https://v1static.nogifes.jp/resource/Movie/LiveBg/",
    "high_live_bg": "https://v1static.nogifes.jp/resource/Movie/HighLiveBg/",
    "other_movie": "https://v1static.nogifes.jp/resource/Movie/Other/",
    "high_other_movie": "https://v1static.nogifes.jp/resource/Movie/HighOtherMovie/",
    "adventure_movie": "https://v1static.nogifes.jp/resource/Movie/AdventureMovie/",
    "member_movie": "https://v1static.nogifes.jp/resource/Movie/Member/",
    "unit_movie": "https://v1static.nogifes.jp/resource/Movie/MovieCard/",
    "unit_gacha_movie": "https://v1static.nogifes.jp/resource/Movie/UnitGachaMovie/",
    "live_finish_movie": "https://v1static.nogifes.jp/resource/Movie/LiveFinishMovie/",
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
    "adventure_movie": "/mnt/data/downloads/nogifes/adventure_movie/",
    "member_movie": "/mnt/data/downloads/nogifes/member_movie/",
    "unit_movie": "/mnt/data/downloads/nogifes/unit_movie/",
    "unit_gacha_movie": "/mnt/data/downloads/nogifes/unit_gacha_movie/",
    "live_finish_movie": "/mnt/data/downloads/nogifes/live_finish_movie/",
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
DOWNLOAD_RETRIES = 3
REQUEST_TIMEOUT = 30
HTTP_SESSION = requests.Session()

def sanitize_filename(title: str) -> str:
    name = title
    for k, v in FILENAME_REPLACEMENTS.items():
        name = name.replace(k, v)

    name = re.sub(r'[\\*?]', "", name)
    name = name.strip().rstrip(". ")

    return name or "untitled"

def download(url: str, file_name: str) -> bool:
    os.makedirs(TEMP_DIR, exist_ok=True)
    file_path = os.path.join(TEMP_DIR, file_name)

    for attempt in range(1, DOWNLOAD_RETRIES + 1):
        try:
            with HTTP_SESSION.get(url, stream=True, timeout=REQUEST_TIMEOUT) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("Content-Length", 0))

                with open(file_path, "wb") as f, tqdm.tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=file_name.ljust(32),
                ) as progress:
                    for chunk in response.iter_content(chunk_size=8192):
                        if not chunk:
                            continue
                        f.write(chunk)
                        progress.update(len(chunk))
            return True
        except (requests.RequestException, OSError) as e:
            print(f"[{attempt}/{DOWNLOAD_RETRIES}] {file_name} download failed: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)

    return False

def extract_cpk(file_path: str) -> bool:
    print(f"Extracting CPK {file_path}...")
    try:
        cpk = CPK(file_path)
        cpk.extract()
    except Exception as e:
        print(f"{file_path} extraction failed: {e}")
        return False

    return True

def extract_usm(file_path: str) -> list[str]:
    print(f"Extracting USM {file_path}...")

    try:
        usm = USM(file_path, KEY)
        usm.extract(TEMP_DIR)

        usm_data = usm.get_metadata()
        stream_data = usm_data[0]["CRIUSF_DIR_STREAM"]

        return [
            f"{TEMP_DIR}/{item['filename'][1]}".replace("D:\\", "").replace("F:\\", "").replace("K:\\", "")
            for item in stream_data[1:]
        ]
    except Exception as e:
        print(f"{file_path} extraction failed: {e}")
        return []

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
    file_list = []
    env = UnityPy.load(file_path)

    for obj in env.objects:
        if obj.type.name == "Texture2D":
            data = obj.parse_as_object()
            dest = os.path.join(TEMP_DIR, f"{data.m_Name}.png")
            data.image.save(dest)
            file_list.append(dest)

    return file_list

def run_cmd(cmd: list[str], show_output: bool = True, check: bool = False) -> str:
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

    return_code = process.wait()
    output = "".join(output_lines)
    if check and return_code != 0:
        raise subprocess.CalledProcessError(return_code, cmd, output=output)
    return output


@functools.cache
def ffmpeg_has_libfdk_aac() -> bool:
    try:
        return "libfdk_aac" in run_cmd(["ffmpeg", "-encoders"], False, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def remux_video(video_path: str, audio_path: str | None, output_path: str) -> bool:
    print(f"Remuxing {video_path}, {audio_path}...")

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if audio_path is None:
            run_cmd(["ffmpeg", "-y", "-i", video_path, "-c:v", "copy", output_path], False, check=True)
        else:
            audio_codec = "libfdk_aac" if ffmpeg_has_libfdk_aac() else "aac"
            run_cmd([
                "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
                "-c:v", "copy", "-c:a", audio_codec, "-b:a", "256k", output_path
            ], False, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, OSError) as e:
        print(f"{video_path} remux failed: {e}")
        return False

def write_complete(dir_path: str):
    with open(os.path.join(dir_path, ".complete"), "w") as f:
        f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")

def check_complete(dir_path: str) -> bool:
    return os.path.exists(os.path.join(dir_path, ".complete"))

def normalize_unicode(text: str) -> str:
    return jaconv.h2z(text, kana=True, ascii=False, digit=False)
