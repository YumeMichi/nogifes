import shutil

from master_data import *
from utils import *

def download_focus_movie(girl_id: int):
    girl_data = get_girl_by_girl_id(girl_id)
    unit_data = get_unit_by_girl_id(girl_id)

    match_index = 0
    for unit in unit_data:
        if "[F]" in unit["unit_name"] and unit["rarity"] % 2 == 1:
            match_index += 1

            movie_data = get_focus_movie_by_unit_id(unit["unit_id"])
            movie_name = f"{movie_data['focus_movie_name']} ({movie_data['live_name']})"
            movie_file_name = f"focus_data_{movie_data["focus_movie_id"]:05d}.cpk"
            movie_url = f"{RESOURCE_PATH['focus_movie']}{movie_file_name}"
            movie_save_name = f"{match_index}、{sanitize_filename(movie_name)}.mp4"
            movie_save_path = f"{DOWNLOAD_PATH["focus_movie"]}{girl_data["girl_name"]}/{movie_save_name}"

            if movie_data["high_quality"] == 1:
                movie_save_path = f"{DOWNLOAD_PATH["high_focus_movie"]}{girl_data["girl_name"]}/{movie_save_name}"
                movie_file_name = f"focus_data_high_{movie_data["focus_movie_id"]:05d}.cpk"
                movie_url = f"{RESOURCE_PATH['high_focus_movie']}{movie_file_name}"

            movie = {
                "movie_id": movie_data["focus_movie_id"],
                "movie_name": movie_name,
                "movie_url": movie_url,
                "movie_file_name": movie_file_name,
                "movie_save_name": movie_save_name,
                "movie_save_path": movie_save_path,
                "high_quality": movie_data["high_quality"]
            }
            print(movie)

            if os.path.exists(movie_save_path):
                print(f"{movie_save_name} already exists")
                continue

            cpk_path = os.path.join(TEMP_DIR, movie_file_name)
            if os.path.exists(cpk_path):
                os.remove(cpk_path)

            if download(movie_url, movie_file_name):
                if extrack_cpk(cpk_path):
                    extracted_path = cpk_path[:-4]
                    movie_path = f"{extracted_path}/movie"
                    music_path = f"{extracted_path}/music"
                    if extract_usm(movie_path) and extract_acb(music_path):
                        video_path = f"{TEMP_DIR}/movie.264_med"
                        audio_path = f"{TEMP_DIR}/0.wav"
                        if remux_video(video_path, audio_path, movie_save_path):
                            os.remove(video_path)
                            os.remove(audio_path)
                            os.remove(cpk_path)
                            shutil.rmtree(extracted_path)
                            print(f"Successfully extracted {movie_save_name}")

if __name__ == "__main__":
    girl_data = get_girl_list()
    for girl in girl_data:
        download_focus_movie(girl["girl_id"])
