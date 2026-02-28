import json

from typing import Any

MASTER_DATA_PATH = "./1.0/masterdata/"

# ================ Common ================
def load_master_data(data_name: str) -> list[Any]:
    with open(MASTER_DATA_PATH + data_name + ".json") as f:
        data = json.load(f)

    return data

# ================ GirlMaster ================
def get_girl_list() -> list[Any]:
    return load_master_data("GirlMaster")

def get_girl_map() -> dict[int, str]:
    data = get_girl_list()
    girl_map: dict[int, str] = {}
    for item in data:
        girl_map[item["girl_id"]] = item["girl_name"].replace(" ", "")

    return girl_map

def get_girl_by_girl_id(girl_id: int) -> dict[str, Any] | None:
    data = load_master_data("GirlMaster")

    for item in data:
        if item["girl_id"] == girl_id:
            item["girl_name"] = item["girl_name"].replace(" ", "")
            return item

    return None

# ================ UnitMaster ================
def get_unit_list() -> list[Any]:
    return load_master_data("UnitMaster")

def get_unit_by_girl_id(girl_id: int) -> list[Any]:
    data = load_master_data("UnitMaster")

    unit_data: list[Any] = []
    for item in data:
        if item["girl_id1"] == girl_id or item["girl_id2"] == girl_id:
            unit_data.append(item)

    return unit_data

def get_unit_girl_list() -> dict[str, list[str]]:
    data = load_master_data("UnitMaster")
    girl_data = get_girl_map()

    unit_girl_list: dict[str, list[str]] = {}
    for item in data:
        girl_name: list[str] = []
        girl_name.append(girl_data[item["girl_id1"]])

        if item["girl_id2"] != 0:
            girl_name.append(girl_data[item["girl_id2"]])

        unit_girl_list[item["unit_id"]] = girl_name

    return unit_girl_list

# ================ FocusMovieMaster ================
def get_focus_movie_by_unit_id(unit_id: int) -> dict[str, Any] | None:
    data = load_master_data("FocusMovieMaster")

    for item in data:
        for unit in item["unit_data"]:
            if unit["unit_id"] == unit_id:
                return item

    return None

# ================ RewardMovieMaster ================
def get_reward_movie_list() -> list[Any]:
    return load_master_data("RewardMovieMaster")

def get_reward_movie_by_unit_id(unit_id: int) -> dict[str, Any] | None:
    data = get_reward_movie_list()

    for item in data:
        for unit in item["unit_data"]:
            if unit["unit_id"] == unit_id:
                return item

    return None

# ================ LiveBgMaster ================
def get_live_bg_list() -> list[Any]:
    return load_master_data("LiveBgMaster")

# ================ ResourceMaster ================
def get_resource_list() -> list[Any]:
    return load_master_data("ResourceMaster")

# ================ OtherMovieMaster ================
def get_other_movie_list() -> list[Any]:
    return load_master_data("OtherMovieMaster")
