import re

from focus_movie import update_movie_data
from master_data import *
from utils import *

MEMBER_MOVIE_DATA_PATH = "data/member_movie.json"

def download_member_movie():
    girl_map = get_girl_map()

    for girl_id in girl_map:
        movie_file_name = f"member_standing_movie_{girl_id:04d}.usme"
        movie_url = f"{RESOURCE_PATH['member_movie']}{movie_file_name}"
        movie_save_name = f"{girl_map[girl_id]}.mp4"
        movie_save_path = f"{DOWNLOAD_PATH["member_movie"]}{movie_save_name}"

        movie = {
            "movie_id": girl_id,
            "movie_name": girl_map[girl_id],
        }

        if os.path.exists(movie_save_path):
            # print(f"{movie_save_name} already exists")
            continue

        usme_path = os.path.join(TEMP_DIR, movie_file_name)
        if os.path.exists(usme_path):
            os.remove(usme_path)

        if download(movie_url, movie_file_name):
            file_list = extract_usm(usme_path)
            print(file_list)
            if len(file_list) > 0:
                video_path = file_list[0]
                if remux_video(video_path, None, movie_save_path):
                    os.remove(video_path)
                    os.remove(usme_path)
                    update_movie_data(MEMBER_MOVIE_DATA_PATH, movie)
                    print(f"Successfully extracted {movie_save_name}")

if __name__ == '__main__':
    download_member_movie()
