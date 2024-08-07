""" utils fonctions """
import base64
import json
from typing import Any
import pygame
import settings


def read_b64_json_file(file_name: str) -> Any:
    """ read a json b64 encoded text file
    return a python object """
    with open(file=file_name, mode='r', encoding='UTF-8') as file:
        b64_encoded = file.read()
        json_string = base64.b64decode(b64_encoded.encode()).decode()
        return json.loads(json_string)


def write_encode_string(file_name: str, data: Any) -> None:
    """ encode a string in json then in b64 and write it to file """
    with open(file=file_name, mode='w', encoding='UTF-8') as file:
        json_data = json.dumps(data)
        b64_encoded_str: str = base64.b64encode(json_data.encode()).decode()
        file.write(b64_encoded_str)


def load_highscore() -> None:
    """ attemp to load  the highscore file and store into settings.highscore """
    try:
        settings.highscore = read_b64_json_file(file_name='highscore')
    except FileNotFoundError:
        # if the file is not found, create it with hiscore 0
        settings.highscore = {'manu': 0,}
        write_encode_string(file_name='highscore', data=settings.highscore)


def save(score: float) -> None:
    """ save the highscore to file """
    score_data = {
        'manu': int(score)
    }
    score_json: str = json.dumps(score_data)
    encoded_json: str = base64.b64encode(score_json.encode()).decode()
    with open(file='highscore', mode='w', encoding='UTF-8') as highscore_file:
        highscore_file.write(encoded_json)
