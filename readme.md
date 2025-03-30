# ⚡ Hanchu Scraper

This project uses **Selenium + FastAPI** to log into a website, scrape energy usage data, and serve it via a simple API. It's Dockerized using **Docker Compose** so you can run it easily. I also include the RESTful api configuration to allow the API to integrate directly into home assistant.

<a href="https://buymeacoffee.com/codenamechicken" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

---

## 📦 Requirements

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 🚀 Quick Start

### 1. Clone the Repo

```bash
git clone https://github.com/iamsteve/hanchu-scraper.git
cd hanchu-scraper
```

### 2. Set Environment Variables

Create a `.env` file in the `app/` folder:

```env
HANCHU_USERNAME=your_username
HANCHU_PASSWORD=your_password
LOGIN_URL=https://iess3.hanchuess.com/login
```

> 🔐 Never share your `.env` file publicly.

---

### 3. Build and Run

```bash
docker-compose up --build
```

To run in the background:

```bash
docker-compose up -d
```

---

### 4. Access the API

Once running, visit:

```
http://<your_ip_or_hostname>:5322/api/data
```

This will return JSON like:

```json
{
  "solar_production": "0.000",
  "home_usage": "0.00432",
  "grid_status": "Idle",
  "grid_usage": "0.000",
  "grid_production": "0.000",
  "battery_export": "0.000",
  "battery_import": "0.000",
  "battery_status": "Discharge",
  "battery_percentage": "67"
}
```

---

## 🏠 Home Assistant Integration

To integrate this scraper with Home Assistant, add the following RESTful sensors to your `configuration.yaml`.  
Replace the URL with the IP or hostname of the device running the scraper (e.g. `http://localhost:5322/api/data`).

```yaml
rest:
  resource: http://<your_ip_or_hostname>:5322/api/data
  sensor:
    - name: "Solar Production"
      value_template: "{{ value_json.solar_production }}"
      device_class: "energy"
      unit_of_measurement: "kWh"
      state_class: "total_increasing"
    - name: "Home Usage"
      value_template: "{{ value_json.home_usage }}"
      device_class: "energy"
      unit_of_measurement: "kWh"
      state_class: "total_increasing"
    - name: "Grid Status"
      value_template: "{{ value_json.grid_status }}"
    - name: "Grid Import"
      value_template: "{{ value_json.grid_usage }}"
      device_class: "energy"
      unit_of_measurement: "kWh"
      state_class: "total_increasing"
    - name: "Grid Export"
      value_template: "{{ value_json.grid_production }}"
      device_class: "energy"
      unit_of_measurement: "kWh"
      state_class: "total_increasing"
    - name: "Battery Discharge"
      value_template: "{{ value_json.battery_export }}"
      device_class: "energy"
      unit_of_measurement: "kWh"
      state_class: "total_increasing"
    - name: "Battery Charge"
      value_template: "{{ value_json.battery_import }}"
      device_class: "energy"
      unit_of_measurement: "kWh"
      state_class: "total_increasing"
    - name: "Battery Status"
      value_template: "{{ value_json.battery_status }}"
    - name: "Battery Level"
      value_template: "{{ value_json.battery_level }}"
      device_class: "battery"
      unit_of_measurement: "%"
```

> 💡 Don’t forget to restart Home Assistant after updating your configuration!

---

## 🛑 Stopping the App

To stop and remove the containers:

```bash
docker-compose down
```

---

## 🧪 Development Notes

- The app logs in using Selenium, fetches data from the dashboard, and updates every 30 seconds.
- The latest data is stored in a text file (`readable_span_contents.txt`) and served via FastAPI.
- Headless Chrome runs inside Docker for scraping.

---

## 📁 Project Structure

```
hanchu-scraper/
├── app/
│   ├── main.py                 # Main script
│   ├── .env                    # Credentials (not committed)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚙️ Troubleshooting
- **Running Home Assistant in Docker?** Make sure you make your docker network available between containers, and when referencing the IP of the scraper, use the container name.
- **Chrome errors?** Make sure your Dockerfile has the correct Chromium and `chromedriver` installed.
- **Login issues?** Confirm your credentials and `LOGIN_URL` are correct in the `.env` file.
- **Permission denied on `.env`?** Ensure the file is readable inside the container (`chmod 644 app/.env`).

---

## 📬 Questions or Help?

Open an issue or reach out!  
Happy scraping! 😄
