import re

from focus_movie import update_movie_data
from master_data import *
from utils import *

SPLASH_MOVIE_DATA_PATH = "data/splash_movie.json"

def download_splash_movie():
    splash_movie_data = get_splash_movie_list()

    for movie_data in splash_movie_data:
        # Skip splash images
        if movie_data['splash_type'] == 2:
            continue

        movie_name = f"splash_movie_{movie_data['splash_id']:05d}"
        movie_file_name = f"{movie_name}.usme"
        movie_url = build_resource_url("splash_movie", movie_file_name)
        movie_save_name = f"{movie_name}.mp4"
        movie_save_path = build_download_path("splash_movie", movie_save_name)

        movie = {
            "movie_id": movie_data['splash_id'],
            "movie_name": movie_name,
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
                audio_path = file_list[1]
                if remux_video(video_path, audio_path, movie_save_path):
                    os.remove(video_path)
                    os.remove(audio_path)
                    os.remove(usme_path)
                    update_movie_data(SPLASH_MOVIE_DATA_PATH, movie)
                    print(f"Successfully extracted {movie_save_name}")

if __name__ == '__main__':
    download_splash_movie()
