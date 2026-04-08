import shutil

from master_data import *
from utils import *

FOCUS_MOVIE_DATA_PATH = "data/focus_movie.json"
REWARD_FOCUS_MOVIE_DATA_PATH = "data/reward_focus_movie.json"

def download_focus_movie(girl_id: int):
    girl_data = get_girl_by_girl_id(girl_id)
    unit_data = get_unit_by_girl_id(girl_id)

    match_index = 0
    for unit in unit_data:
        if "[F]" in unit["unit_name"] and unit["rarity"] % 2 == 1:
            match_index += 1

            movie_data = get_focus_movie_by_unit_id(unit["unit_id"])
            movie_name = f"{movie_data['focus_movie_name']} ({movie_data['live_name']})"
            movie_file_name = f"focus_data_{movie_data["focus_movie_id"]:05d}.cpk"
            movie_url = build_resource_url("focus_movie", movie_file_name)
            movie_save_name = f"{match_index}、{sanitize_filename(movie_name)}.mp4"
            movie_save_path = build_download_path("focus_movie", girl_data["girl_name"], movie_save_name)

            if movie_data["high_quality"] == 1:
                movie_save_path = build_download_path("high_focus_movie", girl_data["girl_name"], movie_save_name)
                movie_file_name = f"focus_data_high_{movie_data["focus_movie_id"]:05d}.cpk"
                movie_url = build_resource_url("high_focus_movie", movie_file_name)

            movie = {
                "movie_id": movie_data["focus_movie_id"],
                "movie_name": normalize_unicode(movie_data["focus_movie_name"]),
                "live_name": normalize_unicode(movie_data["live_name"]),
                "live_date": movie_data["live_date"],
                "live_location": normalize_unicode(movie_data["live_location"]),
                "high_quality": movie_data["high_quality"],
                "girl_name": girl_data["girl_name"],
            }

            if os.path.exists(movie_save_path):
                # print(f"{movie_save_name} already exists")
                continue

            cpk_path = temp_path(movie_file_name)
            if os.path.exists(cpk_path):
                os.remove(cpk_path)

            if download(movie_url, movie_file_name):
                if extract_cpk(cpk_path):
                    extracted_path = os.path.splitext(cpk_path)[0]
                    movie_path = os.path.join(extracted_path, "movie")
                    music_path = os.path.join(extracted_path, "music")
                    file_list = extract_usm(movie_path)
                    if len(file_list) > 0 and extract_acb(music_path):
                        video_path = file_list[0]
                        audio_path = temp_path("0.wav")
                        if remux_video(video_path, audio_path, movie_save_path):
                            os.remove(video_path)
                            os.remove(audio_path)
                            os.remove(cpk_path)
                            shutil.rmtree(extracted_path)
                            update_movie_data(FOCUS_MOVIE_DATA_PATH, movie)
                            print(f"Successfully extracted {movie_save_name}")

def download_reward_focus_movie(girl_id: int):
    girl_data = get_girl_by_girl_id(girl_id)
    unit_data = get_unit_by_girl_id(girl_id)

    for unit in unit_data:
        movie_data = get_reward_movie_by_unit_id(unit["unit_id"])

        if movie_data is None:
            continue

        if "[F]" in movie_data["reward_movie_name"]:
            movie_name_parts = movie_data["reward_movie_name"].split("<br />")
            if len(movie_name_parts) > 1:
                sub_movie_name, main_movie_name = movie_data["reward_movie_name"].split("<br />")
                sub_movie_name = sub_movie_name.replace("全ツ", "真夏の全国ツアー")
                movie_name = f"{main_movie_name} ({sub_movie_name})"
            else:
                movie_name = movie_name_parts[0].replace("全ツ", "真夏の全国ツアー")

            movie_name = re.sub(
                r"\[F\]|\s*SP(?: MOVIE|フルフォーカスMOVIE|ライブフォーカスMOVIE|ライブMOVIE|ﾌﾙﾌｫｰｶｽMOVIE|ﾌｫｰｶｽMOVIE)",
                "",
                movie_name
            )

            movie_file_name = f"reward_movie_{movie_data["reward_movie_id"]:05d}.usme"
            movie_url = build_resource_url("reward_movie", movie_file_name)
            movie_save_name = f"{sanitize_filename(movie_name)}.mp4"
            movie_save_path = build_download_path("reward_focus_movie", girl_data["girl_name"], movie_save_name)

            movie = {
                "movie_id": movie_data["reward_movie_id"],
                "movie_name": normalize_unicode(movie_data["reward_movie_name"]),
                "girl_name": girl_data["girl_name"],
            }

            if os.path.exists(movie_save_path):
                # print(f"{movie_save_name} already exists")
                continue

            usme_path = temp_path(movie_file_name)
            if os.path.exists(usme_path):
                os.remove(usme_path)

            if download(movie_url, movie_file_name):
                file_list = extract_usm(usme_path)
                if len(file_list) > 0:
                    video_path = file_list[0]
                    audio_path = file_list[1] if len(file_list) > 1 else None
                    if remux_video(video_path, audio_path, movie_save_path):
                        os.remove(video_path)
                        if audio_path:
                            os.remove(audio_path)
                        os.remove(usme_path)
                        update_movie_data(REWARD_FOCUS_MOVIE_DATA_PATH, movie)
                        print(f"Successfully extracted {movie_save_name}")

def update_movie_data(json_path: str, json_data: dict):
    data = []
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    else:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

    for i, item in enumerate(data):
        if item["movie_id"] == json_data["movie_id"]:
            data[i] = json_data
            break
    else:
        data.append(json_data)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")

if __name__ == "__main__":
    girl_data = get_girl_list()
    for girl in girl_data:
        download_focus_movie(girl["girl_id"])
        download_reward_focus_movie(girl["girl_id"])
