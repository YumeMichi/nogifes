from focus_movie import update_movie_data
from master_data import *
from utils import *

UNIT_MOVIE_DATA_PATH = "data/unit_movie.json"

def download_unit_movie():
    unit_movie_data = get_unit_movie_list()
    unit_girl_data = get_unit_girl_list()

    for movie_data in unit_movie_data:
        movie_name = movie_data["unit_movie_name"]
        girl_name = "、".join(unit_girl_data[movie_data["unit_data"][0]["unit_id"]])
        movie_file_name = f"movie_card_{movie_data["unit_movie_id"]:05d}.usme"
        movie_url = f"{RESOURCE_PATH['unit_movie']}{movie_file_name}"
        movie_save_name = f"{movie_name}.mp4"
        movie_save_path = f"{DOWNLOAD_PATH["unit_movie"]}{girl_name}/{movie_save_name}"

        movie = {
            "movie_id": movie_data["unit_movie_id"],
            "movie_name": movie_name,
            "girl_name": girl_name,
        }

        if os.path.exists(movie_save_path):
            # print(f"{movie_save_name} already exists")
            continue

        usme_path = os.path.join(TEMP_DIR, movie_file_name)
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
    download_unit_movie()
