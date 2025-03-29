import os
import time
import json
import threading
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import nest_asyncio

# Load environment variables
load_dotenv()

USERNAME = os.getenv("HANCHU_USERNAME")
PASSWORD = os.getenv("HANCHU_PASSWORD")
LOGIN_URL = os.getenv("LOGIN_URL")

if not USERNAME or not PASSWORD or not LOGIN_URL:
    raise EnvironmentError("Missing required environment variables.")

# Constants
DATA_FILE = 'readable_span_contents.txt'
FETCH_INTERVAL = 30  # seconds
WATT_CONVERSION = 1000
DIVISOR = 120

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# FastAPI setup
app = FastAPI()
data_lock = threading.Lock()

@app.get("/api/data")
def get_data():
    with data_lock:
        try:
            with open(DATA_FILE, 'r') as f:
                return JSONResponse(content=json.load(f))
        except Exception as e:
            logging.error(f"Failed to read data: {e}")
            return JSONResponse(content={"error": "Failed to fetch data"}, status_code=500)

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--remote-debugging-port=9222")
    return webdriver.Chrome(options=options)

def login(driver):
    logging.info("Attempting login...")
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 20)

    wait.until(EC.presence_of_element_located((By.ID, "account"))).find_element(By.TAG_NAME, "input").send_keys(USERNAME)
    wait.until(EC.presence_of_element_located((By.ID, "pwd"))).find_element(By.TAG_NAME, "input").send_keys(PASSWORD)
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login-btn"))).click()

def extract_float(text):
    try:
        return float(text)
    except ValueError:
        return 0.0

def truncate_decimal(value):
    value_str = f"{value:.10f}"
    for i, char in enumerate(value_str):
        if char != '0' and char != '.':
            return value_str[:i+3]
    return "0.000"

def fetch_data(driver):
    wait = WebDriverWait(driver, 10)

    scene = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "scene")))
    spans = scene.find_elements(By.TAG_NAME, "span")
    stream_images = scene.find_elements(By.CLASS_NAME, "stream-img")

    bat_status = scene.find_element(By.CLASS_NAME, "bat-status").text
    unit = scene.find_element(By.CLASS_NAME, "unit").text
    battery_percentage = scene.find_element(By.CLASS_NAME, "progress-wrap").find_element(By.CLASS_NAME, "text").text.replace('.0%', '')

    grid_status = "Idle"
    grid_production = 0.0
    grid_usage = 0.0

    for img in stream_images:
        src = img.get_attribute("src")
        if "grid-in" in src:
            grid_status = "Importing"
            grid_usage = extract_float(spans[5].text)
            break
        elif "grid-out" in src:
            grid_status = "Exporting"
            grid_production = extract_float(spans[5].text)
            break

    solar = extract_float(spans[1].text)
    home = extract_float(spans[3].text)

    battery_export = 0.0
    battery_import = 0.0
    battery_flow = extract_float(spans[7].text)

    if bat_status == "Charge":
        battery_import = battery_flow
    elif bat_status == "Discharge":
        battery_export = battery_flow

    unit_multiplier = WATT_CONVERSION if unit == "W" else 1
    convert = lambda x: (x / DIVISOR) / unit_multiplier

    result = {
        'solar_production': truncate_decimal(convert(solar)),
        'home_usage': truncate_decimal(convert(home)),
        'grid_status': grid_status,
        'grid_usage': truncate_decimal(convert(grid_usage)),
        'grid_production': truncate_decimal(convert(grid_production)),
        'battery_export': truncate_decimal(convert(battery_export)),
        'battery_import': truncate_decimal(convert(battery_import)),
        'battery_status': bat_status,
        'battery_percentage': battery_percentage
    }

    with data_lock:
        with open(DATA_FILE, 'w') as f:
            json.dump(result, f, indent=4)

    logging.info("Data fetched and saved.")

def run_monitor():
    driver = create_driver()
    try:
        login(driver)
        fetch_data(driver)
        time.sleep(FETCH_INTERVAL)

        while True:
            try:
                driver.refresh()
                fetch_data(driver)
            except Exception as e:
                logging.warning(f"Error occurred: {e}. Retrying login.")
                login(driver)
                fetch_data(driver)
            time.sleep(FETCH_INTERVAL)
    finally:
        driver.quit()

def start_server():
    uvicorn.run(app, host="0.0.0.0", port=5322)

# Bootstrap
nest_asyncio.apply()
threading.Thread(target=start_server, daemon=True).start()
run_monitor()
