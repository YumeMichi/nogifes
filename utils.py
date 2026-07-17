import datetime
import functools
import jaconv
import json
import os
import re
import requests
import shutil
import subprocess
import tqdm
import UnityPy

from pathlib import Path
from PyCriCodecs import ACB, CPK, USM
from config import DOWNLOAD_ROOT, STATIC_BASE_URL

KEY = 0x0013F11BC5510101

RESOURCE_PATH = {
    "asset_bundle": f"{STATIC_BASE_URL}/resource/Android_2017_4_1f1/",
    "focus_movie": f"{STATIC_BASE_URL}/resource/Movie/Focus/",
    "high_focus_movie": f"{STATIC_BASE_URL}/resource/Movie/HighFocusMovie/",
    "reward_movie": f"{STATIC_BASE_URL}/resource/Movie/Reward/",
    "live_bg": f"{STATIC_BASE_URL}/resource/Movie/LiveBg/",
    "high_live_bg": f"{STATIC_BASE_URL}/resource/Movie/HighLiveBg/",
    "other_movie": f"{STATIC_BASE_URL}/resource/Movie/Other/",
    "high_other_movie": f"{STATIC_BASE_URL}/resource/Movie/HighOtherMovie/",
    "adventure_movie": f"{STATIC_BASE_URL}/resource/Movie/AdventureMovie/",
    "member_movie": f"{STATIC_BASE_URL}/resource/Movie/Member/",
    "unit_movie": f"{STATIC_BASE_URL}/resource/Movie/MovieCard/",
    "unit_gacha_movie": f"{STATIC_BASE_URL}/resource/Movie/UnitGachaMovie/",
    "live_finish_movie": f"{STATIC_BASE_URL}/resource/Movie/LiveFinishMovie/",
    "splash_movie": f"{STATIC_BASE_URL}/resource/Splash/Movie/",
}

DOWNLOAD_PATH = {
    "member_card": DOWNLOAD_ROOT / "member_card",
    "member_standing": DOWNLOAD_ROOT / "member_standing",
    "focus_movie": DOWNLOAD_ROOT / "focus_movie",
    "high_focus_movie": DOWNLOAD_ROOT / "high_focus_movie",
    "reward_focus_movie": DOWNLOAD_ROOT / "reward_focus_movie",
    "live_bg": DOWNLOAD_ROOT / "live_bg",
    "high_live_bg": DOWNLOAD_ROOT / "high_live_bg",
    "other_movie": DOWNLOAD_ROOT / "other_movie",
    "high_other_movie": DOWNLOAD_ROOT / "high_other_movie",
    "reward_movie": DOWNLOAD_ROOT / "reward_movie",
    "adventure_movie": DOWNLOAD_ROOT / "adventure_movie",
    "member_movie": DOWNLOAD_ROOT / "member_movie",
    "unit_movie": DOWNLOAD_ROOT / "unit_movie",
    "unit_gacha_movie": DOWNLOAD_ROOT / "unit_gacha_movie",
    "live_finish_movie": DOWNLOAD_ROOT / "live_finish_movie",
    "splash_movie": DOWNLOAD_ROOT / "splash_movie",
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

TEMP_DIR = Path("temp")
DOWNLOAD_RETRIES = 3
REQUEST_TIMEOUT = 30
HTTP_SESSION = requests.Session()

def build_resource_url(resource_key: str, *parts: str) -> str:
    base = RESOURCE_PATH[resource_key]
    suffix = "/".join(str(part).strip("/\\") for part in parts if part)
    return f"{base}{suffix}" if suffix else base

def build_download_path(path_key: str, *parts: str) -> str:
    return str(DOWNLOAD_PATH[path_key].joinpath(*(str(part) for part in parts)))

def temp_path(*parts: str) -> str:
    return str(TEMP_DIR.joinpath(*(str(part) for part in parts)))

def _normalize_stream_filename(stream_file_name: str) -> str:
    # USM metadata may escape "#" as "\#". This should stay in filename.
    path_value = stream_file_name.replace("\\#", "#")
    path_value = path_value.replace("\\", "/")
    path_value = re.sub(r"/+", "/", path_value)
    if len(path_value) > 1 and path_value[1] == ":":
        path_value = path_value[2:]
    return path_value.lstrip("/")

def _stream_path_candidates(stream_file_name: str) -> list[Path]:
    normalized = _normalize_stream_filename(stream_file_name)
    if not normalized:
        return []

    normalized_path = Path(normalized)
    parts = normalized_path.parts

    # Build candidates from full relative path down to basename-only path.
    candidates: list[Path] = []
    for i in range(len(parts)):
        candidates.append(TEMP_DIR.joinpath(*parts[i:]))

    # Keep order and remove duplicates.
    uniq_candidates: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        uniq_candidates.append(candidate)
    return uniq_candidates

def _resolve_stream_output_path(stream_file_name: str) -> str:
    normalized = _normalize_stream_filename(stream_file_name)
    if normalized:
        # Some extractors keep Windows-style path separators in the filename itself.
        literal_windows_path = TEMP_DIR / normalized.replace("/", "\\")
        if literal_windows_path.exists():
            return str(literal_windows_path)

    candidates = _stream_path_candidates(stream_file_name)
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    file_name = Path(normalized).name if normalized else ""
    if file_name:
        for candidate in TEMP_DIR.rglob(file_name):
            return str(candidate)

    if candidates:
        return str(candidates[0])

    normalized = _normalize_stream_filename(stream_file_name)
    if normalized:
        return temp_path(normalized)
    return temp_path(Path(stream_file_name).name)

def sanitize_filename(title: str) -> str:
    name = title
    for k, v in FILENAME_REPLACEMENTS.items():
        name = name.replace(k, v)

    name = re.sub(r'[\\*?]', "", name)
    name = name.strip().rstrip(". ")

    return name or "untitled"

def download(url: str, file_name: str) -> bool:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    file_path = TEMP_DIR / file_name

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
            if file_path.exists():
                file_path.unlink()

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
        usm.extract(str(TEMP_DIR))

        usm_data = usm.get_metadata()
        stream_data = usm_data[0]["CRIUSF_DIR_STREAM"]

        return [
            _resolve_stream_output_path(item["filename"][1])
            for item in stream_data[1:]
        ]
    except Exception as e:
        print(f"{file_path} extraction failed: {e}")
        return []

def extract_acb(file_path: str) -> bool:
    print(f"Extracting ACB {file_path}...")
    try:
        acb = ACB(file_path)
        acb.extract(True, KEY, str(TEMP_DIR))
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
            dest = TEMP_DIR / f"{data.m_Name}.png"
            data.image.save(str(dest))
            file_list.append(str(dest))

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
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

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

def _remove_file(path: str | Path) -> None:
    Path(path).unlink(missing_ok=True)

def download_usm_movie(
    url: str,
    archive_name: str,
    output_path: str | Path,
    *,
    include_audio: bool = True,
    require_audio: bool = False,
) -> bool:
    """Download a USME file, remux its streams, and clean up on success."""
    destination = Path(output_path)
    if destination.exists():
        return False

    archive_path = TEMP_DIR / archive_name
    _remove_file(archive_path)
    if not download(url, archive_name):
        return False

    stream_paths = extract_usm(str(archive_path))
    if not stream_paths:
        return False

    video_path = stream_paths[0]
    audio_path = stream_paths[1] if include_audio and len(stream_paths) > 1 else None
    if require_audio and audio_path is None:
        print(f"{archive_path} does not contain an audio stream")
        return False

    if not remux_video(video_path, audio_path, str(destination)):
        return False

    _remove_file(video_path)
    if audio_path is not None:
        _remove_file(audio_path)
    _remove_file(archive_path)
    print(f"Successfully extracted {destination.name}")
    return True

def download_cpk_movie(url: str, archive_name: str, output_path: str | Path) -> bool:
    """Download a CPK movie bundle, remux it, and clean up on success."""
    destination = Path(output_path)
    if destination.exists():
        return False

    archive_path = TEMP_DIR / archive_name
    _remove_file(archive_path)
    if not download(url, archive_name) or not extract_cpk(str(archive_path)):
        return False

    extracted_path = archive_path.with_suffix("")
    stream_paths = extract_usm(str(extracted_path / "movie"))
    audio_path = TEMP_DIR / "0.wav"
    if not stream_paths or not extract_acb(str(extracted_path / "music")):
        return False

    if not remux_video(stream_paths[0], str(audio_path), str(destination)):
        return False

    _remove_file(stream_paths[0])
    _remove_file(audio_path)
    _remove_file(archive_path)
    shutil.rmtree(extracted_path, ignore_errors=True)
    print(f"Successfully extracted {destination.name}")
    return True

def update_json_record(json_path: str | Path, record: dict, identifier_key: str) -> None:
    """Upsert a downloaded asset record while retaining the existing JSON format."""
    path = Path(json_path)
    data: list[dict] = []
    if path.exists():
        try:
            loaded_data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded_data, list):
                data = loaded_data
        except json.JSONDecodeError:
            pass
    else:
        path.parent.mkdir(parents=True, exist_ok=True)

    for index, item in enumerate(data):
        if item.get(identifier_key) == record[identifier_key]:
            data[index] = record
            break
    else:
        data.append(record)

    path.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")

def write_complete(dir_path: str):
    with open(Path(dir_path) / ".complete", "w") as f:
        f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")

def check_complete(dir_path: str) -> bool:
    return (Path(dir_path) / ".complete").exists()

def normalize_unicode(text: str) -> str:
    return jaconv.h2z(text, kana=True, ascii=False, digit=False)
