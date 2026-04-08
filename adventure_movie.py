import re

from focus_movie import update_movie_data
from master_data import *
from utils import *

ADVENTURE_MOVIE_DATA_PATH = "data/adventure_movie.json"

def download_adventure_movie():
    resource_data = get_resource_list()

    for res in resource_data:
        if "adventure_movie" in res["filename"]:
            movie_id = res["filename"].split("_")[2][:-5]
            movie_file_name = res["filename"]
            movie_url = build_resource_url("adventure_movie", movie_file_name)
            movie_save_name = f"{movie_file_name[:-5]}.mp4"
            movie_save_path = build_download_path("adventure_movie", movie_save_name)

            movie = {
                "movie_id": movie_id,
                "movie_name": movie_file_name[:-5],
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
                        update_movie_data(ADVENTURE_MOVIE_DATA_PATH, movie)
                        print(f"Successfully extracted {movie_save_name}")

if __name__ == '__main__':
    download_adventure_movie()
