import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1485336699482542232/XDaPfTe8xnPV7Jq7kbpV9auCmEPqukHoowL3vpvSZYguQU48mfiINUmziSfaka8v66PW"

DB = "cars.db"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TIMEOUT = 10

# ---------- DATABASE ----------

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id TEXT PRIMARY KEY,
        title TEXT,
        vin TEXT,
        first_seen TEXT,
        last_seen TEXT,
        platforms TEXT,
        current_price TEXT
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        car_id TEXT,
        price TEXT,
        date TEXT
    )
    """)
    conn.close()

# ---------- HELPERS ----------

def generate_id(title, mileage):
    base = f"{title}-{mileage}"
    return hashlib.md5(base.encode()).hexdigest()

def now():
    return datetime.utcnow().isoformat()

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        return r.text
    except Exception as e:
        print("Fetch failed:", e)
        return None

# ---------- SCORING SYSTEM ----------

def score_vehicle(price, mileage):
    score = 50

    try:
        price_val = int(price.replace("$","").replace(",",""))
        mileage_val = int(mileage.replace(",","").split()[0])

        if price_val < 65000:
            score += 20
        if mileage_val < 20000:
            score += 15
        if mileage_val < 10000:
            score += 10

    except:
        pass

    return min(score, 100)

# ---------- DATABASE LOGIC ----------

def upsert_car(car):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT * FROM cars WHERE id=?", (car["id"],))
    existing = cur.fetchone()

    if not existing:
        print("NEW CAR:", car["title"])

        cur.execute("""
        INSERT INTO cars VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            car["id"],
            car["title"],
            car["vin"],
            now(),
            now(),
            car["platform"],
            car["price"]
        ))

        cur.execute("""
        INSERT INTO price_history VALUES (?, ?, ?)
        """, (car["id"], car["price"], now()))

        send_alert(car, "NEW")

    else:
        existing_price = existing[6]

        if existing_price != car["price"]:
            print("PRICE CHANGE:", car["title"])

            cur.execute("""
            UPDATE cars SET current_price=?, last_seen=? WHERE id=?
            """, (car["price"], now(), car["id"]))

            cur.execute("""
            INSERT INTO price_history VALUES (?, ?, ?)
            """, (car["id"], car["price"], now()))

            send_alert(car, "PRICE CHANGE")

        # update platforms
        platforms = set(existing[5].split(","))
        platforms.add(car["platform"])

        cur.execute("""
        UPDATE cars SET platforms=?, last_seen=? WHERE id=?
        """, (",".join(platforms), now(), car["id"]))

    conn.commit()
    conn.close()

# ---------- ALERT ----------

def send_alert(car, event):
    score = score_vehicle(car["price"], car["mileage"])

    msg = f"""
🚨 {event} QUADRIFOGLIO

{car['title']}
💰 {car['price']}
📏 {car['mileage']}
📊 Score: {score}/100
🌐 Source: {car['platform']}

{car['link']}
"""

    requests.post(DISCORD_WEBHOOK, json={"content": msg})

# ---------- SCRAPERS ----------

def scrape_cars():
    url = "https://www.cars.com/shopping/results/?makes[]=alfa_romeo&models[]=alfa_romeo-giulia&trim_levels[]=quadrifoglio"

    html = fetch(url)
    if not html:
        return

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select('[data-testid="vehicle-card"]')

    print("Cars.com:", len(cards))

    for c in cards:
        try:
            title = c.select_one('[data-testid="vehicle-card-title"]').text.strip()
            price = c.select_one('[data-testid="vehicle-card-price"]').text.strip()
            mileage_tag = c.select_one('[data-testid="vehicle-card-mileage"]')
            mileage = mileage_tag.text.strip() if mileage_tag else "0"

            link = "https://www.cars.com" + c.select_one("a")["href"]

            car_id = generate_id(title, mileage)

            upsert_car({
                "id": car_id,
                "title": title,
                "price": price,
                "mileage": mileage,
                "vin": None,
                "platform": "Cars.com",
                "link": link
            })

        except Exception as e:
            print("Cars.com error:", e)

def scrape_bat():
    url = "https://bringatrailer.com/alfa-romeo/giulia/"

    html = fetch(url)
    if not html:
        return

    soup = BeautifulSoup(html, "html.parser")
    listings = soup.select(".listing-card")

    print("BaT:", len(listings))

    for l in listings:
        try:
            title = l.select_one(".listing-card__title").text.strip()
            price = l.select_one(".listing-card__price").text.strip()
            mileage = "0"

            link = l.select_one("a")["href"]

            car_id = generate_id(title, mileage)

            upsert_car({
                "id": car_id,
                "title": title,
                "price": price,
                "mileage": mileage,
                "vin": None,
                "platform": "Bring a Trailer",
                "link": link
            })

        except Exception as e:
            print("BaT error:", e)

# ---------- MAIN ----------

def run():
    import requests

    print("Sending test message...")

    r = requests.post(DISCORD_WEBHOOK, json={
        "content": "🚨 BOT TEST — if you see this, Discord works 🚨"
    })

    print("Status:", r.status_code)
