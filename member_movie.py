from master_data import get_girl_map
from utils import (
    build_download_path,
    build_resource_url,
    download_usm_movie,
    update_json_record,
)

MEMBER_MOVIE_DATA_PATH = "data/member_movie.json"


def download_member_movie() -> None:
    for girl_id, girl_name in get_girl_map().items():
        movie_file_name = f"member_standing_movie_{girl_id:04d}.usme"
        movie_url = build_resource_url("member_movie", movie_file_name)
        movie_save_name = f"{girl_name}.mp4"
        movie_save_path = build_download_path("member_movie", movie_save_name)
        movie = {"movie_id": girl_id, "movie_name": girl_name}

        if download_usm_movie(movie_url, movie_file_name, movie_save_path, include_audio=False):
            update_json_record(MEMBER_MOVIE_DATA_PATH, movie, "movie_id")


if __name__ == "__main__":
    download_member_movie()
