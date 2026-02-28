import shutil

from master_data import *
from utils import *

LIVE_BG_RESOURCE_TYPE = [
    8,  # Low-quality
    33  # High-quality
]

LIVE_BG_DATA_PATH = "data/live_bg.json"

def download_live_bg():
    live_bg_data = get_live_bg_list()
    resource_data = get_resource_list()

    for live_bg in live_bg_data:
        if live_bg["live_bg_type"] == 1:
            for resource in resource_data:
                if (
                    resource["sub_id"] == live_bg["live_bg_id"] and
                    resource["resource_type"] in LIVE_BG_RESOURCE_TYPE
                ):
                    bg_id = live_bg["live_bg_id"]
                    bg_name = live_bg["live_bg_name"]
                    bg_high_quality = 0
                    bg_file_name = resource["filename"]
                    bg_url = f"{RESOURCE_PATH["live_bg"]}{bg_file_name}"
                    if resource["resource_type"] == 33:
                        bg_url = f"{RESOURCE_PATH["high_live_bg"]}{bg_file_name}"
                        bg_high_quality = 1
                    bg_save_name = f"{sanitize_filename(bg_name)}.mp4"
                    if live_bg["live_name"] != "--":
                        bg_save_name = f"{sanitize_filename(f"{bg_name} ({live_bg["live_name"]})")}.mp4"
                    bg_save_path = f"{DOWNLOAD_PATH['live_bg']}{bg_save_name}"
                    if resource["resource_type"] == 33:
                        bg_save_path = f"{DOWNLOAD_PATH['high_live_bg']}{bg_save_name}"

                    bg = {
                        "live_bg_id": bg_id,
                        "live_bg_name": bg_name,
                        "live_bg_has_high_quality": bg_high_quality
                    }

                    if os.path.exists(bg_save_path):
                        # print(f"{bg_save_path} already exists")
                        continue

                    cpk_path = os.path.join(TEMP_DIR, bg_file_name)
                    if os.path.exists(cpk_path):
                        os.remove(cpk_path)

                    if download(bg_url, bg_file_name):
                        if extrack_cpk(cpk_path):
                            extracted_path = cpk_path[:-4]
                            movie_path = f"{extracted_path}/movie"
                            music_path = f"{extracted_path}/music"
                            if extract_usm(movie_path) and extract_acb(music_path):
                                video_path = f"{TEMP_DIR}/movie.264_med"
                                audio_path = f"{TEMP_DIR}/0.wav"
                                if remux_video(video_path, audio_path, bg_save_path):
                                    os.remove(video_path)
                                    os.remove(audio_path)
                                    os.remove(cpk_path)
                                    shutil.rmtree(extracted_path)
                                    update_live_bg_data(LIVE_BG_DATA_PATH, bg)
                                    print(f"Successfully extracted {bg_save_name}")

def update_live_bg_data(json_path: str, json_data: dict):
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        data = []

    for i, item in enumerate(data):
        if item["live_bg_id"] == json_data["live_bg_id"]:
            data[i] = json_data
            break
    else:
        data.append(json_data)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")

if __name__ == '__main__':
    download_live_bg()
