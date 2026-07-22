from master_data import get_girl_map
from utils import (
    build_download_path,
    build_resource_url,
    download_usm_movie,
    load_download_records,
    should_download_record,
    update_json_record,
)

MEMBER_MOVIE_DATA_PATH = "data/member_movie.json"


def download_member_movie(*, force: bool = False) -> None:
    downloaded_movies = load_download_records(MEMBER_MOVIE_DATA_PATH, "movie_id")
    for girl_id, girl_name in get_girl_map().items():
        movie_file_name = f"member_standing_movie_{girl_id:04d}.usme"
        movie_url = build_resource_url("member_movie", movie_file_name)
        movie_save_name = f"{girl_name}.mp4"
        movie_save_path = build_download_path("member_movie", movie_save_name)
        movie = {"movie_id": girl_id, "movie_name": girl_name}

        if not force and not should_download_record(downloaded_movies, movie, "movie_id"):
            continue

        if download_usm_movie(movie_url, movie_file_name, movie_save_path, include_audio=False, force=force):
            update_json_record(MEMBER_MOVIE_DATA_PATH, movie, "movie_id")
            downloaded_movies[movie["movie_id"]] = movie


if __name__ == "__main__":
    download_member_movie()
