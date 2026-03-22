import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1485336699482542232/XDaPfTe8xnPV7Jq7kbpV9auCmEPqukHoowL3vpvSZYguQU48mfiINUmziSfaka8v66PW"

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 10

def send_alert(msg):
    print("Sending alert...")
    r = requests.post(DISCORD_WEBHOOK, json={"content": msg})
    print("Discord status:", r.status_code)

# ---------- CarGurus ----------
def scrape_cargurus():
    print("Scraping CarGurus...")

    url = "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?entitySelectingHelper.selectedEntity=d1750&trimNames=Quadrifoglio"

    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        print("CarGurus page loaded")
    except Exception as e:
        print("CarGurus failed:", e)
        return

    soup = BeautifulSoup(r.text, "html.parser")
    listings = soup.select(".cg-dealFinder-result-wrap")

    print("CarGurus listings:", len(listings))

    if len(listings) == 0:
        print("⚠️ CarGurus returned 0 listings")

    for l in listings[:5]:
        try:
            title = l.select_one("h4").text.strip()
            price = l.select_one(".cg-dealFinder-priceAndMoPayment").text.strip()
            mileage = l.select_one(".cg-dealFinder-mileage").text.strip()

            link = "https://www.cargurus.com" + l.select_one("a")["href"]

            msg = f"""
🚨 CarGurus Listing

{title}
💰 {price}
📏 {mileage}

{link}
"""
            send_alert(msg)

        except Exception as e:
            print("CarGurus parse error:", e)

# ---------- iSeeCars ----------
def scrape_iseecars():
    print("Scraping iSeeCars...")

    url = "https://www.iseecars.com/used_cars-t24726-used-alfa-romeo-giulia-quadrifoglio-for-sale"

    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        print("iSeeCars page loaded")
    except Exception as e:
        print("iSeeCars failed:", e)
        return

    soup = BeautifulSoup(r.text, "html.parser")
    listings = soup.select("article")

    print("iSeeCars listings:", len(listings))

    for l in listings[:5]:
        try:
            title = l.text.strip()[:120]

            msg = f"""
🚨 iSeeCars Listing

{title}
"""
            send_alert(msg)

        except Exception as e:
            print("iSeeCars parse error:", e)

# ---------- MAIN ----------
def run():
    print("BOT STARTED")

    scrape_cargurus()
    scrape_iseecars()

    print("DONE")

if __name__ == "__main__":
    run()
