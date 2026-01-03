from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from starlette.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
from pytz import timezone

from app.database import init_db, get_html_content, load_tournaments
from app.tasks import update_data_task


# --- Lifespan Manager ---
# This is the modern FastAPI way to handle startup/shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize DB
    init_db()

    # 2. Start Scheduler
    poland_tz = timezone("Europe/Warsaw")

    scheduler = BackgroundScheduler(timezone=poland_tz)

    # Use "cron" instead of "interval"
    scheduler.add_job(
        update_data_task,
        trigger="cron",
        hour=22,
        minute=0,
        id="daily_update"
    )

    scheduler.start()

    # 3. Run immediately on startup so data is available
    update_data_task()

    yield  # Application runs here

    # 4. Cleanup (Shutdown scheduler)
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


# --- Routes ---

@app.get("/latest_html", response_class=HTMLResponse)
def get_html():
    html = get_html_content()
    if not html:
        raise HTTPException(status_code=404, detail="No data available yet")
    return html


@app.get("/tournaments")
def get_tournaments_api():
    tournaments = load_tournaments()
    if not tournaments:
        raise HTTPException(status_code=404, detail="No data available")
    return tournaments


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)