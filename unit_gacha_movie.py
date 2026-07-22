from master_data import get_unit_girl_list, get_unit_list
from utils import (
    build_download_path,
    build_resource_url,
    download_usm_movie,
    load_download_records,
    should_download_record,
    update_json_record,
)

UNIT_GACHA_MOVIE_DATA_PATH = "data/unit_gacha_movie.json"


def download_unit_gacha_movie() -> None:
    unit_girl_data = get_unit_girl_list()
    downloaded_movies = load_download_records(UNIT_GACHA_MOVIE_DATA_PATH, "movie_id")
    for unit in get_unit_list():
        if unit["gacha_movie"] != 1:
            continue

        movie_name = unit["unit_name"]
        girl_name = "、".join(unit_girl_data[unit["unit_id"]])
        movie_file_name = f"unit_gacha_movie_{unit['unit_id']:07d}.usme"
        movie_url = build_resource_url("unit_gacha_movie", movie_file_name)
        movie_save_name = f"{movie_name}.mp4"
        movie_save_path = build_download_path("unit_gacha_movie", girl_name, movie_save_name)
        movie = {"movie_id": unit["unit_id"], "movie_name": movie_name, "girl_name": girl_name}

        if not should_download_record(downloaded_movies, movie, "movie_id"):
            continue

        if download_usm_movie(movie_url, movie_file_name, movie_save_path, include_audio=False):
            update_json_record(UNIT_GACHA_MOVIE_DATA_PATH, movie, "movie_id")
            downloaded_movies[movie["movie_id"]] = movie


if __name__ == "__main__":
    download_unit_gacha_movie()
