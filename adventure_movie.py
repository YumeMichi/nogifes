from master_data import get_resource_list
from utils import (
    build_download_path,
    build_resource_url,
    download_usm_movie,
    update_json_record,
)

ADVENTURE_MOVIE_DATA_PATH = "data/adventure_movie.json"


def download_adventure_movie() -> None:
    for resource in get_resource_list():
        movie_file_name = resource["filename"]
        if "adventure_movie" not in movie_file_name:
            continue

        movie_id = movie_file_name.split("_")[2][:-5]
        movie_url = build_resource_url("adventure_movie", movie_file_name)
        movie_save_name = f"{movie_file_name[:-5]}.mp4"
        movie_save_path = build_download_path("adventure_movie", movie_save_name)
        movie = {"movie_id": movie_id, "movie_name": movie_file_name[:-5]}

        if download_usm_movie(movie_url, movie_file_name, movie_save_path):
            update_json_record(ADVENTURE_MOVIE_DATA_PATH, movie, "movie_id")


if __name__ == "__main__":
    download_adventure_movie()
