import os
import json
import platform
import urllib.request


def clear():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


def download_file_from_url(url: str, location: str, file_name: str = None):
    if file_name is None:
        file_name = url.split("/")[-1]

    urllib.request.urlretrieve(url, f"{location}/{file_name}")


def get_urls_from_file(file: str):
    urls = []
    with open(file) as f:
        for line in f:
            if not line == '\n' and not line.__contains__('#'):
                urls.append(line.strip())
    return urls


def get_slugs_from_file(file: str):
    slugs = []
    with open(file) as f:
        for line in f:
            if not line == '\n' and not line.__contains__('#'):
                slugs.append(get_slug_from_url(line))
    return slugs


def get_slug_from_url(url: str):
    return url.strip().split('/')[-1]


def format_json(json_string: str):
    return json.dumps(json_string, indent=4, sort_keys=True)
