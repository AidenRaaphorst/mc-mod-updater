import os
import json
import pathlib
import urllib.request
import urllib.parse
import requests


def download_file_from_url(url: str, directory: str = None, file_name: str = None):
    if file_name is None:
        file_name = get_file_name_from_url(url)

    r = requests.get(url)

    if directory is None:
        with open(f"{file_name}", 'wb') as outfile:
            outfile.write(r.content)
    else:
        if not os.path.exists(directory):
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

        with open(f"{directory}/{file_name}", 'wb') as outfile:
            outfile.write(r.content)


def get_slug_from_url(url: str):
    return url.strip().split('/')[-1]


def get_file_name_from_url(url: str):
    file_name = url.strip().split('/')[-1]
    return urllib.parse.unquote(file_name)


def format_json(json_string: str):
    return json.dumps(json_string, indent=4, sort_keys=True)
