import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1485336699482542232/XDaPfTe8xnPV7Jq7kbpV9auCmEPqukHoowL3vpvSZYguQU48mfiINUmziSfaka8v66PW"

def send_alert(msg):
    print("🚨 ATTEMPTING TO SEND ALERT")
    r = requests.post(DISCORD_WEBHOOK, json={"content": msg})
    print("Discord status:", r.status_code)

def test_discord():
    print("Testing Discord directly...")
    send_alert("🚨 DIRECT TEST MESSAGE 🚨")

def scrape_cars():
    print("Scraping Cars.com...")

    url = "https://www.cars.com/shopping/results/?makes[]=alfa_romeo&models[]=alfa_romeo-giulia&trim_levels[]=quadrifoglio"

    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        print("Page loaded, length:", len(r.text))
    except Exception as e:
        print("Request failed:", e)
        return

    soup = BeautifulSoup(r.text, "html.parser")

    cars = soup.select('[data-testid="vehicle-card"]')

    print("Cars found:", len(cars))

    if len(cars) == 0:
        print("⚠️ NO CARS FOUND — SELECTOR BROKEN OR BLOCKED")

    for c in cars[:3]:  # only test first 3
        try:
            title = c.select_one('[data-testid="vehicle-card-title"]').text.strip()
            print("Found car:", title)

            send_alert(f"TEST CAR FOUND: {title}")

        except Exception as e:
            print("Parse error:", e)

def run():
    print("BOT STARTED")

    test_discord()   # 👈 THIS MUST FIRE
    scrape_cars()

    print("DONE")

run()
