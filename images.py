import requests
import shutil
import os
from animal import Animal
from typing import List
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CUSTOM_SEARCH_API_KEY = str(os.environ.get(
    "GOOGLE_CUSTOM_SEARCH_API_KEY"))
GOOGLE_CUSTOM_SEARCH_CX = str(os.environ.get("GOOGLE_CUSTOM_SEARCH_CX"))
GOOGLE_IMG_SEARCH_API_URL = 'https://customsearch.googleapis.com/customsearch/v1?cx={cx}&exactTerms={query}&fileType=jpg&imgSize=LARGE&imgType=photo&searchType=image&key={api_key}'
ASSETS_PATH = 'Assets/'
ACTIVE_PATH = 'Active/'


def download_images(animals: List[Animal]):
    print("downloading images...")
    for animal in animals:
        path = ASSETS_PATH + animal.name + "/"
        query_keyword = animal.name.replace(" ", "%20")
        print(query_keyword)
        res = requests.get(url=GOOGLE_IMG_SEARCH_API_URL.format(cx=GOOGLE_CUSTOM_SEARCH_CX,
                                                                query=query_keyword, api_key=GOOGLE_CUSTOM_SEARCH_API_KEY))
        res = res.json()
        if not os.path.exists(path):
            os.makedirs(path)
        for index, item in enumerate(res['items']):
            print(item["link"])
            res2 = requests.get(item["link"], stream=True)
            if res2.status_code == 200:
                file_count = len([f for f in os.listdir(
                    path) if os.path.isfile(path + f)])

                filename = str(file_count) + ".jpg"
                full_path = path + filename
                if not os.path.exists(full_path):
                    with open(full_path, 'wb') as f:
                        shutil.copyfileobj(res2.raw, f)
                    print(filename + " Successfully Downloaded in " + path)
                else:
                    print("Image already downloaded.")
                activate_image(path, filename)
            else:
                print("Image could not be retrieved.")


def activate_image(directory, filename):
    active_directory = directory + ACTIVE_PATH
    active_path = active_directory + filename
    if not os.path.exists(active_directory):
        os.makedirs(directory + ACTIVE_PATH)
    if not os.path.exists(active_path):
        shutil.copy(directory + filename, active_path)


def get_image_count(animal):
    path = animal.name
    return len([name for name in os.listdir(path) if os.path.isfile(name)])
