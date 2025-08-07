import requests
from bs4 import BeautifulSoup
import re
import os

URL = "https://dota2.ru" 

headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0"
}


def parse_dota2(path:str):
    resp  = requests.get(URL+path, headers=headers)

    content = resp.content
    return BeautifulSoup(content, "html.parser")

def save_in_dir(dirname, for_save):
    SAVE_DIR = dirname

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    for name, image in for_save:
        try:
            img_response = requests.get(image, headers=headers)
            img_response.raise_for_status()

            # Очищаем имя героя для использования в имени файла
            # Заменяем недопустимые символы (например, пробелы, слэши) на подчеркивания
            safe_hero_name = re.sub(r'[^\w\-]', '_', name.strip())
            
           
            # Определяем расширение файла из URL (например, .png или .jpg)
            file_extension = os.path.splitext(image)[1] or ".png"  # По умолчанию .png, если не удалось определить

            if not any(file_extension.endswith(i) for i in [".jpg", '.png', '.webp', '.jpeg']):
                file_extension = file_extension.split("?")[0]

            # Формируем путь к файлу
            file_path = os.path.join(SAVE_DIR, f"{safe_hero_name}{file_extension}")
            with open(file_path, "wb") as f:
                f.write(img_response.content)
                print(f"Сохранено: {file_path}")

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке изображения для {name}: {e}")
        except Exception as e:
            print(f"Ошибка при сохранении изображения для {name}: {e}")

def parse_heroes():
    soup = parse_dota2("/heroes")
    all_heroes = soup.find_all("a", class_="base-hero__link-hero")

    names_images = [(i.get("data-tooltipe"),URL+i.find("img").get("src")) for i in all_heroes]

    save_in_dir("dota2_heroes", names_images)

def format_number(a):
    return ''.join([i for i in a if a.isdigit()])

def parse_items():
    soup = parse_dota2("/items")
    items_soup = soup.find_all("li", class_="base-items__shop-item js-items-filter-item")
    price_list = [{
        i.get("data-item-name") : 
        format_number(i.find("div",class_="base-items__shop-descr-wrap")
        # .find("div", class_="base-items__shop-descr-top caster")
        .find_all("p")[-1].text.strip())
        for i in items_soup}]
    
    names_items = [(i.get("data-item-name"),URL+i.find("img").get("src")) for i in items_soup]
    # save_in_dir("dota2_items", names_items)
    return price_list

import json
with open("price_items.json", "w") as f:
    json.dump(parse_items(), f, indent=4)