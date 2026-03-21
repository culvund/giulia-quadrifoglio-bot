import sqlite3
import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1484970505818734702/-p581hwWVQn9tdFyacio6PBOHlhwQ0gRQm4406s2Y99NQszpgBHtz05YZwLf3oAh-3KO"

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
    print("Bot started")

    init_db()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        print("Requesting page...")
        r = requests.get(SEARCH_URL, headers=headers, timeout=10)
        print("Page loaded")
    except Exception as e:
        print("Request failed:", e)
        return

    soup = BeautifulSoup(r.text, "html.parser")

    cars = soup.select('[data-testid="vehicle-card"]')

    print(f"Found {len(cars)} cars")

    for car in cars:
        try:
            link = "https://www.cars.com" + car.select_one("a")["href"]
            title = car.select_one('[data-testid="vehicle-card-title"]').text.strip()
            price = car.select_one('[data-testid="vehicle-card-price"]').text.strip()

            mileage_tag = car.select_one('[data-testid="vehicle-card-mileage"]')
            mileage = mileage_tag.text.strip() if mileage_tag else "N/A"

            image = car.select_one("img")["src"]

            print("Checking:", title)

            if not seen(link):
                print("NEW CAR FOUND")
                save(link)
                alert(title, price, mileage, link, image)

        except Exception as e:
            print("ERROR:", e)
