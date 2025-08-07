from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import os
import random
import re

app = FastAPI()

app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешённые домены
    allow_credentials=True,
    allow_methods=["GET"],  # Разрешённые методы
    allow_headers=["*"],  # Разрешённые заголовки
)


def get_path(name):
    DIR = name
    path = Path(DIR).resolve()
    return path

import json
def load_item_prices():
    try:
        with open("price_items.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="File items_prices.json not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format in items_prices.json")

item_prices = load_item_prices()

def get_item_price(name, price_filter = 0):
    price = item_prices[0].get(name)
    if str(price).isdigit() or isinstance(price, int):
        price = int(price)
        if price >= price_filter:
            return price
        else:
            return False
    return None


path = get_path("dota2_heroes")
all_heroes = [i for i in os.walk(path)][0][2]
app.mount("/img", StaticFiles(directory=path), name="dota_imges")

path2 = get_path("dota2_items")
all_items = [i for i in os.walk(path2)][0][2]
good_items = [i for i in all_items if get_item_price(i.split(".")[0], 2000)]
app.mount("/items", StaticFiles(directory=path2), name="dota_items")

@app.get("/get_hero")
async def get_random_hero():
    get_random = random.choice(all_heroes)
    return {
        "hero": get_random.split(".")[0],
        "url" : "/img/"+get_random
    }

@app.get("/get_hero_with_build")
async def get_random_hero_with_build():
    get_random_hero = random.choice(all_heroes)
    
    get_random_build = set()
    while len(get_random_build) < 6:
        get_random_build.add(random.choice(good_items))
    return {
        "hero": get_random_hero.split(".")[0],
        "url" : "/img/"+get_random_hero,
        "build": [
            {"item_title": i.split(".")[0],
             "item_url": "/items/"+ i,
             "price": get_item_price(i.split(".")[0])}
            for i in get_random_build]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Используем PORT из окружения Render
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)  # reload=False для продакшена
