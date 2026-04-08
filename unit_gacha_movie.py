from focus_movie import update_movie_data
from master_data import *
from utils import *

UNIT_MOVIE_DATA_PATH = "data/unit_gacha_movie.json"

def download_unit_gacha_movie():
    unit_data = get_unit_list()
    unit_girl_data = get_unit_girl_list()

    for unit in unit_data:
        if unit["gacha_movie"] == 1:
            movie_name = unit["unit_name"]
            girl_name = "、".join(unit_girl_data[unit["unit_id"]])
            movie_file_name = f"unit_gacha_movie_{unit["unit_id"]:07d}.usme"
            movie_url = build_resource_url("unit_gacha_movie", movie_file_name)
            movie_save_name = f"{movie_name}.mp4"
            movie_save_path = build_download_path("unit_gacha_movie", girl_name, movie_save_name)

            movie = {
                "movie_id": unit["unit_id"],
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
                    if remux_video(video_path, None, movie_save_path):
                        os.remove(video_path)
                        os.remove(usme_path)
                        update_movie_data(UNIT_MOVIE_DATA_PATH, movie)
                        print(f"Successfully extracted {movie_save_name}")

if __name__ == '__main__':
    download_unit_gacha_movie()
