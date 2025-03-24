# ⚡ Hanchu Scraper

This project uses **Selenium + FastAPI** to log into a website, scrape energy usage data, and serve it via a simple API. It's Dockerized using **Docker Compose** so you can run it easily.

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
http://localhost:5322/api/data
```

This will return JSON like:

```json
{
    "PV Draw": "500 W",
    "Home Use": "450 W",
    "Grid": "50 W",
    "Battery": "90 %"
}
```

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

- **Chrome errors?** Make sure your Dockerfile has the correct Chromium and `chromedriver` installed.
- **Login issues?** Confirm your credentials and `LOGIN_URL` are correct in the `.env` file.
- **Permission denied on `.env`?** Ensure the file is readable inside the container (`chmod 644 app/.env`).

---

## 📬 Questions or Help?

Open an issue or reach out!  
Happy scraping! 😄
