import sqlite3
import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1484967992461754568/1eaw9xCrysJ8X7Bz7gv0FaiVpwQE55lIILX58UN1k0i1kJNJlXxvYSgjlNmQzQRI8q7b"

DB = "database.db"

SEARCH_URL = "https://www.cars.com/shopping/results/?makes[]=alfa_romeo&models[]=alfa_romeo-giulia&trim_levels[]=quadrifoglio"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS listings (id TEXT PRIMARY KEY)")
    conn.close()

def seen(link):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM listings WHERE id=?", (link,))
    exists = cur.fetchone()
    conn.close()
    return exists

def save(link):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO listings (id) VALUES (?)", (link,))
    conn.commit()
    conn.close()

def alert(title, price, mileage, link, image):
    data = {
        "content": f"🚨 {title}\n💰 {price}\n📏 {mileage}\n{link}\n{image}"
    }
    requests.post(DISCORD_WEBHOOK, json=data)

def run():
    init_db()

    r = requests.get(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    cars = soup.select(".vehicle-card")

    for car in cars:
        try:
            link = "https://www.cars.com" + car.select_one("a")["href"]
            title = car.select_one(".title").text.strip()
            price = car.select_one(".primary-price").text.strip()
            mileage = car.select_one(".mileage").text.strip()
            image = car.select_one("img")["src"]

            if not seen(link):
                save(link)
                alert(title, price, mileage, link, image)

        except:
            continue

run()
