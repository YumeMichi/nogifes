import re

from focus_movie import update_movie_data
from master_data import *
from utils import *

REWARD_MOVIE_DATA_PATH = "data/reward_movie.json"

def download_reward_movie():
    reward_movie_data = get_reward_movie_list()
    unit_girl_data = get_unit_girl_list()

    for movie_data in reward_movie_data:
        girl_name = "、".join(unit_girl_data[movie_data["unit_data"][0]["unit_id"]])

        movie_name_parts = movie_data["reward_movie_name"].split("<br />")
        if len(movie_name_parts) > 1:
            sub_movie_name, main_movie_name = movie_data["reward_movie_name"].split("<br />")
            main_movie_name = re.sub(
                r"\[F\]| SP(フルフォーカスMOVIE|ライブフォーカスMOVIE|ライブMOVIE|ﾌﾙﾌｫｰｶｽMOVIE|ﾌｫｰｶｽMOVIE)",
                "",
                main_movie_name
            )

            sub_movie_name = sub_movie_name.replace("全ツ", "真夏の全国ツアー")
            movie_name = f"{main_movie_name} ({sub_movie_name})"
        else:
            movie_name = movie_name_parts[0].replace("全ツ", "真夏の全国ツアー")

        movie_file_name = f"reward_movie_{movie_data["reward_movie_id"]:05d}.usme"
        movie_url = f"{RESOURCE_PATH['reward_movie']}{movie_file_name}"
        movie_save_name = f"{sanitize_filename(movie_name)}.mp4"
        movie_save_path = f"{DOWNLOAD_PATH["reward_movie"]}{girl_name}/{movie_save_name}"

        movie = {
            "movie_id": movie_data["reward_movie_id"],
            "movie_name": normalize_unicode(movie_data["reward_movie_name"]),
            "girl_name": girl_name,
        }

        if os.path.exists(movie_save_path):
            # print(f"{movie_save_name} already exists")
            continue

        usme_path = os.path.join(TEMP_DIR, movie_file_name)
        if os.path.exists(usme_path):
            os.remove(usme_path)

        if download(movie_url, movie_file_name):
            if extract_usm(usme_path):
                video_path = f"{TEMP_DIR}/{movie_file_name[:-5]}.264_med"
                audio_path = f"{TEMP_DIR}/{movie_file_name[:-5]}.avi"
                if movie_data["reward_movie_id"] in [181, 182, 183]:
                    video_path = f"{TEMP_DIR}/{movie_file_name[:-5]}_50.264_med"
                if remux_video(video_path, audio_path, movie_save_path):
                    os.remove(video_path)
                    os.remove(audio_path)
                    os.remove(usme_path)
                    update_movie_data(REWARD_MOVIE_DATA_PATH, movie)
                    print(f"Successfully extracted {movie_save_name}")

if __name__ == '__main__':
    download_reward_movie()
