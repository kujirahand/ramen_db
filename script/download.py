import requests
from flickrapi import FlickrAPI
from urllib.request import urlretrieve
from pprint import pprint
import os, time, sys, json

# set keyword
KEYWORD = "ramen"

# get env
FLICKR_KEY = os.environ.get('FLICKR_KEY', None)
FLICKR_SECRET = os.environ.get('FLICKR_SECRET', None)
WAIT_TIME = 0.5

# 商用利用可能なライセンスIDを設定
commercial_use_licenses = [4, 5, 6, 9, 10]

# test key
if FLICKR_KEY is None or FLICKR_SECRET is None:
    print("please set FLICKR_KEY and FLICKR_SECRET")
    quit()

def download_photos(photos, download_dir):
    for i, photo in enumerate(photos):
        save_file = os.path.join(download_dir, f"{photo['id']}.jpg")
        if os.path.exists(save_file):
            print(f"{i:03d}: Already exists {save_file}")
            continue
        # thumbnail url (q: 150x150)
        url = f"https://farm{photo['farm']}.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}_q.jpg"
        print(f"{i:03d}: Downloading {url}")
        response = requests.get(url)
        if response.status_code == 200:
            # save jpeg
            with open(os.path.join(download_dir, f"{photo['id']}.jpg"), 'wb') as f:
                f.write(response.content)
            # save metadata
            with open(os.path.join(download_dir, f"{photo['id']}.json"), 'w') as f:
                f.write(json.dumps(photo, ensure_ascii=False, indent=2))
        else:
            print(f"Failed to download {url}")
        time.sleep(WAIT_TIME)

# get photo
def get_index(keyword: str, max_photo: int=500) -> list[dict]:
    flickr = FlickrAPI(FLICKR_KEY, FLICKR_SECRET, format='parsed-json')
    save_dir = os.path.join(os.path.dirname(__file__), 'data', keyword)
    os.makedirs(save_dir, exist_ok=True)
    page_id = 1
    max_page = max_photo // 100
    while True:
        print(f"--- page {page_id:03d} / {max_page:03d}---")
        result = flickr.photos.search(
            text = keyword,
            per_page = 100,
            page = page_id,
            media = 'photos',
            sort = 'relevance',
            safe_search = 1,
            license=','.join(map(str, commercial_use_licenses)),
            extras = 'url_q, licence'
        )
        photos = result['photos']
        pprint(photos)
        # download photos
        download_photos(photos['photo'], save_dir)
        if photos['pages'] == page_id or page_id == max_page:
            break
        page_id += 1
        time.sleep(WAIT_TIME)

if __name__ == '__main__':
    get_index(KEYWORD)

