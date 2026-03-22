from playwright.sync_api import sync_playwright
import requests

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1485336699482542232/XDaPfTe8xnPV7Jq7kbpV9auCmEPqukHoowL3vpvSZYguQU48mfiINUmziSfaka8v66PW"

def send_alert(msg):
    print("Sending alert...")
    r = requests.post(DISCORD_WEBHOOK, json={"content": msg})
    print("Discord status:", r.status_code)

def scrape_cargurus(page):
    print("Opening CarGurus...")

    page.goto("https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?entitySelectingHelper.selectedEntity=d1750&trimNames=Quadrifoglio")

    page.wait_for_timeout(5000)

    listings = page.query_selector_all(".cg-dealFinder-result-wrap")

    print("CarGurus listings:", len(listings))

    if len(listings) == 0:
        print("⚠️ Still blocked or selector changed")

    for l in listings[:5]:
        try:
            title = l.query_selector("h4").inner_text()
            price = l.query_selector(".cg-dealFinder-priceAndMoPayment").inner_text()

            msg = f"""
🚨 CarGurus Listing

{title}
💰 {price}
"""
            send_alert(msg)

        except Exception as e:
            print("Parse error:", e)

def run():
    print("BOT STARTED")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        scrape_cargurus(page)

        browser.close()

    print("DONE")

if __name__ == "__main__":
    run()
