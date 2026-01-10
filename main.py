from threading import Thread
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from starlette.responses import HTMLResponse
import uvicorn

from app.database import init_db, get_html_content, load_tournaments
from app.tasks import update_data_task

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield  # Application runs here

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, # type: ignore[arg-type]
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



# --- Routes ---

@app.post('/fetch_tournaments')
def fetch_tournaments():
    thread = Thread(target=update_data_task, daemon=True)
    thread.start()
    return {"status": "started"}

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