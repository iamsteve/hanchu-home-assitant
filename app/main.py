from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import os
import time
import threading
import json
import logging
import nest_asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Validate credentials
USERNAME = os.getenv('HANCHU_USERNAME')
PASSWORD = os.getenv('HANCHU_PASSWORD')
LOGIN_URL = os.getenv('LOGIN_URL')

if not USERNAME or not PASSWORD or not LOGIN_URL:
    raise ValueError("Environment variables HANCHU_USERNAME, HANCHU_PASSWORD, and LOGIN_URL must be set.")

DATA_FILE = 'readable_span_contents.txt'
FETCH_INTERVAL = 30  # seconds

# FastAPI app
app = FastAPI()
data_lock = threading.Lock()

@app.get('/api/data')
def get_data():
    with data_lock:
        try:
            with open(DATA_FILE, 'r') as file:
                data = json.load(file)
            return JSONResponse(content=data)
        except Exception as e:
            logging.error(f"Failed to read data: {e}")
            return JSONResponse(content={"error": "Failed to fetch data"}, status_code=500)

def login(driver):
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 10)

    account_input = wait.until(EC.presence_of_element_located((By.ID, "account"))).find_element(By.TAG_NAME, "input")
    password_input = wait.until(EC.presence_of_element_located((By.ID, "pwd"))).find_element(By.TAG_NAME, "input")

    account_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)

    login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "login-btn")))
    login_button.click()

    logging.info("Login successful.")

def fetch_data(driver):
    wait = WebDriverWait(driver, 10)
    scene_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "scene")))
    span_elements = scene_element.find_elements(By.TAG_NAME, "span")

    if len(span_elements) < 9:
        raise ValueError("Not enough span elements found")

    readable_span_contents = {
        'PV Draw': f"{span_elements[1].text} {span_elements[2].text}",
        'Home Use': f"{span_elements[3].text} {span_elements[4].text}",
        'Grid': f"{span_elements[5].text} {span_elements[6].text}",
        'Battery': f"{span_elements[7].text} {span_elements[8].text}"
    }

    with data_lock:
        with open(DATA_FILE, 'w') as file:
            json.dump(readable_span_contents, file, indent=4)

    logging.info("Data fetched and saved successfully.")

def start_server():
    uvicorn.run(app, host="0.0.0.0", port=5322)

def run_monitor():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        login(driver)
        fetch_data(driver)
        time.sleep(FETCH_INTERVAL)

        while True:
            try:
                driver.refresh()
                fetch_data(driver)
            except Exception as e:
                logging.warning(f"Exception occurred: {e}, retrying login...")
                login(driver)
                fetch_data(driver)
            time.sleep(FETCH_INTERVAL)
    finally:
        driver.quit()

# Run FastAPI server in a thread
nest_asyncio.apply()
threading.Thread(target=start_server, daemon=True).start()

# Start monitor logic
run_monitor()
