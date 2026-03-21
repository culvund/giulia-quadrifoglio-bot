import sqlite3
import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1484970505818734702/-p581hwWVQn9tdFyacio6PBOHlhwQ0gRQm4406s2Y99NQszpgBHtz05YZwLf3oAh-3KO"

DB = "database.db"

SEARCH_URLS = [
    "https://www.cars.com/shopping/results/?makes[]=alfa_romeo&models[]=alfa_romeo-giulia&trim_levels[]=quadrifoglio&maximum_distance=all",
    "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?entitySelectingHelper.selectedEntity=d1750&trimNames=Quadrifoglio"
]

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id TEXT PRIMARY KEY
        )
    """)
    conn.close()

def seen_before(listing_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM listings WHERE id=?", (listing_id,))
    result = cur.fetchone()
    conn.close()
    return result is not None

def save_listing(listing_id):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO listings (id) VALUES (?)", (listing_id,))
    conn.commit()
    conn.close()

def send_alert(title, price, mileage, link, image):
    data = {
        "embeds": [{
            "title": "🚨 New Giulia Quadrifoglio Found",
            "description": f"**{title}**\n💰 {price}\n📏 {mileage}",
            "url": link,
            "image": {"url": image}
        }]
    }
    requests.post(DISCORD_WEBHOOK, json=data)

def scrape_cars(dotcom_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(dotcom_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    listings = soup.select(".vehicle-card")

    for car in listings:
        try:
            link = "https://www.cars.com" + car.select_one("a")["href"]
            title = car.select_one(".title").text.strip()
            price = car.select_one(".primary-price").text.strip()
            mileage = car.select_one(".mileage").text.strip()
            image = car.select_one("img")["src"]

            if not seen_before(link):
                save_listing(link)
                send_alert(title, price, mileage, link, image)

        except Exception:
            continue

def scrape_cargurus(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    listings = soup.select(".cg-dealFinder-result-wrap")

    for car in listings:
        try:
            link = "https://www.cargurus.com" + car.select_one("a")["href"]
            title = car.select_one("h4").text.strip()
            price = car.select_one(".cg-dealFinder-priceAndMoPayment").text.strip()
            mileage = car.select_one(".cg-dealFinder-mileage").text.strip()
            image = car.select_one("img")["src"]

            if not seen_before(link):
                save_listing(link)
                send_alert(title, price, mileage, link, image)

        except Exception:
            continue

def run():
    init_db()
    scrape_cars(SEARCH_URLS[0])
    scrape_cargurus(SEARCH_URLS[1])

if __name__ == "__main__":
    run()
