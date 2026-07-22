from master_data import get_splash_movie_list
from utils import (
    build_download_path,
    build_resource_url,
    download_usm_movie,
    load_download_records,
    should_download_record,
    update_json_record,
)

SPLASH_MOVIE_DATA_PATH = "data/splash_movie.json"


def download_splash_movie() -> None:
    downloaded_movies = load_download_records(SPLASH_MOVIE_DATA_PATH, "movie_id")
    for movie_data in get_splash_movie_list():
        if movie_data["splash_type"] == 2:
            continue

        movie_name = f"splash_movie_{movie_data['splash_id']:05d}"
        movie_file_name = f"{movie_name}.usme"
        movie_url = build_resource_url("splash_movie", movie_file_name)
        movie_save_name = f"{movie_name}.mp4"
        movie_save_path = build_download_path("splash_movie", movie_save_name)
        movie = {"movie_id": movie_data["splash_id"], "movie_name": movie_name}

        if not should_download_record(downloaded_movies, movie, "movie_id"):
            continue

        if download_usm_movie(
            movie_url,
            movie_file_name,
            movie_save_path,
            require_audio=True,
        ):
            update_json_record(SPLASH_MOVIE_DATA_PATH, movie, "movie_id")
            downloaded_movies[movie["movie_id"]] = movie


if __name__ == "__main__":
    download_splash_movie()
