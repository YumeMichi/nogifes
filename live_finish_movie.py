from focus_movie import update_movie_data
from master_data import *
from utils import *

UNIT_MOVIE_DATA_PATH = "data/live_finish_movie.json"

def download_live_finish_movie():
    unit_data = get_unit_list()
    unit_girl_data = get_unit_girl_list()

    for unit in unit_data:
        if unit["gacha_movie"] == 1:
            movie_name = unit["unit_name"]
            girl_name = "、".join(unit_girl_data[unit["unit_id"]])
            movie_file_name = f"live_finish_movie_{unit["live_finish_movie_resource_id"]:07d}.usme"
            movie_url = build_resource_url("live_finish_movie", movie_file_name)
            movie_save_name = f"{movie_name}.mp4"
            movie_save_path = build_download_path("live_finish_movie", girl_name, movie_save_name)

            movie = {
                "movie_id": unit["live_finish_movie_resource_id"],
                "movie_name": movie_name,
                "girl_name": girl_name,
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
                        update_movie_data(UNIT_MOVIE_DATA_PATH, movie)
                        print(f"Successfully extracted {movie_save_name}")

if __name__ == '__main__':
    download_live_finish_movie()
