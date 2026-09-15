"""
Script to capture additional distinct application screenshots for:
05-fleet-telematics-grid.png
06-regulatory-audit-modal.png
07-cascading-disruption-sim.png
08-bob-action-directives.png
"""
import os
import sys
import time
import threading
import uvicorn
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By

# Ensure parent directory in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.backend.main import app

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

def get_driver():
    try:
        edge_options = EdgeOptions()
        edge_options.add_argument("--headless=new")
        edge_options.add_argument("--window-size=1600,1050")
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
        chrome_options.add_argument("--window-size=1600,1050")
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

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)

    driver = get_driver()
    if not driver:
        print("Could not initialize webdriver.")
        return

    try:
        print("Loading application at http://127.0.0.1:8000...")
        driver.get("http://127.0.0.1:8000")
        time.sleep(3)

        # -------------------------------------------------------------
        # Screenshot 05: Fleet Telematics & Redeployment Grid Tab
        # -------------------------------------------------------------
        print("Capturing 05-fleet-telematics-grid.png...")
        fleet_tab = driver.find_element(By.CSS_SELECTOR, '[data-tab="tab-fleet"]')
        fleet_tab.click()
        time.sleep(1.5)
        p5 = os.path.join(screenshots_dir, "05-fleet-telematics-grid.png")
        driver.save_screenshot(p5)
        print(f"Captured: {p5}")

        # -------------------------------------------------------------
        # Screenshot 06: Regulatory Audit Certificate Modal
        # -------------------------------------------------------------
        print("Capturing 06-regulatory-audit-modal.png...")
        cc_tab = driver.find_element(By.CSS_SELECTOR, '[data-tab="tab-coldchain"]')
        cc_tab.click()
        time.sleep(1.5)

        cert_btn = driver.find_element(By.ID, "btn-download-cert")
        cert_btn.click()
        time.sleep(1.5)
        p6 = os.path.join(screenshots_dir, "06-regulatory-audit-modal.png")
        driver.save_screenshot(p6)
        print(f"Captured: {p6}")

        # Close modal
        close_modal_btn = driver.find_element(By.ID, "btn-close-modal")
        close_modal_btn.click()
        time.sleep(1)

        # -------------------------------------------------------------
        # Screenshot 07: Cascading Disruption Simulation on Map
        # -------------------------------------------------------------
        print("Capturing 07-cascading-disruption-sim.png...")
        map_tab = driver.find_element(By.CSS_SELECTOR, '[data-tab="tab-map"]')
        map_tab.click()
        time.sleep(1.5)

        trigger_sim_btn = driver.find_element(By.ID, "btn-trigger-all-disruptions")
        trigger_sim_btn.click()
        time.sleep(2.5)
        p7 = os.path.join(screenshots_dir, "07-cascading-disruption-sim.png")
        driver.save_screenshot(p7)
        print(f"Captured: {p7}")

        # -------------------------------------------------------------
        # Screenshot 08: IBM BoB Copilot Action Directives
        # -------------------------------------------------------------
        print("Capturing 08-bob-action-directives.png...")
        btn_copilot = driver.find_element(By.ID, "btn-toggle-copilot")
        btn_copilot.click()
        time.sleep(1)

        chat_input = driver.find_element(By.ID, "chat-input")
        chat_input.send_keys("Reroute shipment SH-7091 and redeploy nearest reefer")
        send_btn = driver.find_element(By.ID, "btn-chat-send")
        send_btn.click()
        time.sleep(2.5)

        p8 = os.path.join(screenshots_dir, "08-bob-action-directives.png")
        driver.save_screenshot(p8)
        print(f"Captured: {p8}")

        print("\nAll 4 additional screenshots captured successfully!")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
