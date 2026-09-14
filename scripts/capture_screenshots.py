"""
Script to start NexusSupply AI server and capture verified application screenshots
for demo/screenshots/01-home-dashboard.png, 02-query-input.png, 03-result-output.png, 04-cold-chain-excursion.png
"""
import os
import sys
import time
import threading
import uvicorn
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By

# Ensure parent directory in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.backend.main import app

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

def get_driver():
    # Try Edge first (standard on Windows)
    try:
        edge_options = EdgeOptions()
        edge_options.add_argument("--headless=new")
        edge_options.add_argument("--window-size=1600,1000")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--no-sandbox")
        driver = webdriver.Edge(options=edge_options)
        print("Using Edge webdriver")
        return driver
    except Exception as e:
        print(f"Edge failed: {e}, trying Chrome...")

    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1600,1000")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=chrome_options)
        print("Using Chrome webdriver")
        return driver
    except Exception as e:
        print(f"Chrome failed: {e}")
        return None

def main():
    screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "demo", "screenshots"))
    os.makedirs(screenshots_dir, exist_ok=True)

    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)

    driver = get_driver()
    if not driver:
        print("Could not initialize webdriver. Will use fallback generator.")
        return

    try:
        print("Loading application at http://127.0.0.1:8000...")
        driver.get("http://127.0.0.1:8000")
        time.sleep(3)

        # 1. Capture Home Dashboard
        p1 = os.path.join(screenshots_dir, "01-home-dashboard.png")
        driver.save_screenshot(p1)
        print(f"Captured: {p1}")

        # 2. Open BoB Copilot Drawer & send a query
        btn_copilot = driver.find_element(By.ID, "btn-toggle-copilot")
        btn_copilot.click()
        time.sleep(1)

        # Click the first prompt chip
        chips = driver.find_elements(By.CLASS_NAME, "chip-btn")
        if chips:
            chips[0].click()
            time.sleep(2)

        p2 = os.path.join(screenshots_dir, "02-query-input.png")
        driver.save_screenshot(p2)
        print(f"Captured: {p2}")

        # Close drawer
        btn_close = driver.find_element(By.ID, "btn-close-drawer")
        btn_close.click()
        time.sleep(0.5)

        # 3. Re-routing Tab
        tabs = driver.find_elements(By.CLASS_NAME, "tab-btn")
        for tab in tabs:
            if "Re-Routing" in tab.text:
                tab.click()
                break
        time.sleep(1.5)
        p3 = os.path.join(screenshots_dir, "03-result-output.png")
        driver.save_screenshot(p3)
        print(f"Captured: {p3}")

        # 4. Cold Chain Sentinel Tab
        for tab in tabs:
            if "Cold Chain" in tab.text:
                tab.click()
                break
        time.sleep(1.5)
        p4 = os.path.join(screenshots_dir, "04-cold-chain-excursion.png")
        driver.save_screenshot(p4)
        print(f"Captured: {p4}")

        print("All 4 application screenshots captured successfully!")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
