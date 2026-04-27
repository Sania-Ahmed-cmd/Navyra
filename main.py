# ---------------- IMPORTS ----------------
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

from optimization import choose_best_route, get_action

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- INPUT MODEL ----------------
class InputData(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    fuel: float = Field(..., ge=0, le=100)
    service_days: float = Field(..., ge=0)


# ---------------- WEATHER ----------------
def get_weather(lat, lon):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        )
        res = requests.get(url, timeout=3)

        if res.status_code != 200:
            raise Exception("Weather API failed")

        data = res.json()
        cw = data.get("current_weather", {})

        return {
            "wind": cw.get("windspeed", 20),
            "temp": cw.get("temperature", 20)
        }

    except Exception as e:
        print("Weather fallback:", e)
        return {"wind": 20, "temp": 20}


# ---------------- RISK FUNCTIONS ----------------
def fuel_risk(fuel):
    return 1 / (1 + (fuel / 40))


def maintenance_risk(days):
    return min(days / 180, 1)


def weather_risk(wind):
    return min(wind / 40, 1)


def compute_risk(wind, fuel, service_days):
    w = weather_risk(wind)
    f = fuel_risk(fuel)
    m = maintenance_risk(service_days)

    risk = (w**1.3)*0.5 + (f**1.2)*0.25 + (m**1.4)*0.25

    return min(risk, 1), w, f, m


# ---------------- HISTORY STORAGE ----------------
history = {}
MAX_POINTS = 20


# ---------------- ROOT (IMPORTANT FOR RENDER) ----------------
@app.get("/")
def home():
    return {"status": "API running"}


# ---------------- MAIN API ----------------
@app.post("/predict")
def predict(data: InputData):

    key = f"{round(data.lat,2)}_{round(data.lon,2)}"
    now = int(time.time())

    # weather
    weather = get_weather(data.lat, data.lon)

    # risk
    risk, w, f, m = compute_risk(
        weather["wind"],
        data.fuel,
        data.service_days
    )

    # history
    if key not in history:
        history[key] = []

    history[key].append({
        "time": now,
        "risk": round(risk, 3)
    })

    history[key] = history[key][-MAX_POINTS:]

    # status
    if risk > 0.7:
        status = "Critical"
    elif risk > 0.3:
        status = "Warning"
    else:
        status = "Safe"

    # ---------------- ROUTE + ACTION (FIXED PART) ----------------
    try:
        route_data = choose_best_route(risk, "Azzam", weather["wind"])
        action_data = get_action(status, weather)
    except Exception as e:
        print("Route/Action error:", e)
        route_data = {"system_choice": "Default Route"}
        action_data = {"system_action": "Normal Operation"}

    # ---------------- FINAL RESPONSE ----------------
    return {
        "risk": round(risk, 3),
        "status": status,

        # ✅ IMPORTANT (frontend needs these)
        "route": route_data.get("system_choice", "Default Route"),
        "action": action_data.get("system_action", "Normal Operation"),

        "components": {
            "weather": round(w, 2),
            "fuel": round(f, 2),
            "maintenance": round(m, 2)
        },

        "state": {
            "fuel": data.fuel,
            "service_days": data.service_days
        },

        "weather": weather,
        "history": history[key]
    }


# ---------------- EXTRA ROUTES ----------------
@app.get("/route")
def route(ship: str, risk: float, wind: float):
    return choose_best_route(risk, ship, wind)


@app.get("/action")
def action(status: str, wind: float):
    return get_action(status, {"wind": wind})