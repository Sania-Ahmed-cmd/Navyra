# ---------------- IMPORTS ----------------
import os

# Safe Gemini import
try:
    import google.generativeai as genai
except:
    genai = None


# ---------------- GEMINI SETUP ----------------
api_key = os.getenv("GEMINI_API_KEY")

if genai and api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
else:
    model = None


# ---------------- ROUTES ----------------
routes = {
    "Azzam": [
        {"name": "North Corridor", "weather_sensitivity": 0.8, "congestion": 0.6, "distance": 1.0},
        {"name": "Mid Sea Route", "weather_sensitivity": 0.5, "congestion": 0.4, "distance": 1.1},
        {"name": "Storm Belt Route", "weather_sensitivity": 1.3, "congestion": 0.3, "distance": 0.9}
    ],
    "Dilbar": [
        {"name": "Coastal Route", "weather_sensitivity": 0.6, "congestion": 0.7, "distance": 1.0},
        {"name": "Deep Sea Route", "weather_sensitivity": 0.9, "congestion": 0.3, "distance": 1.2}
    ],
    "Eclipse": [
        {"name": "Atlantic Lane", "weather_sensitivity": 0.8, "congestion": 0.5, "distance": 1.0},
        {"name": "Southern Drift", "weather_sensitivity": 0.6, "congestion": 0.4, "distance": 1.2}
    ]
}


# ---------------- WEATHER EXPOSURE ----------------
def compute_weather_exposure(wind, sensitivity):
    return min((wind / 40) * sensitivity, 1)


# ---------------- GEMINI HELPER ----------------
def ask_gemini(prompt):
    if not model:
        return "AI unavailable"

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI error: {str(e)}"


# ---------------- ROUTE OPTIMIZATION ----------------
def choose_best_route(base_risk, ship_name, wind):

    if ship_name not in routes:
        return {
            "system_choice": "DEFAULT ROUTE",
            "ai_advice": "No AI suggestion"
        }

    best = None
    best_score = float("inf")

    for r in routes[ship_name]:
        weather_exp = compute_weather_exposure(wind, r["weather_sensitivity"])

        score = (
            base_risk * weather_exp +
            r["congestion"] * 0.3 +
            r["distance"] * 0.2
        )

        if score < best_score:
            best_score = score
            best = r["name"]

    # 🔥 AI ADVICE
    prompt = f"""
    Ship: {ship_name}
    Wind: {wind}
    Risk: {base_risk}

    System chose route: {best}

    Do you agree? Suggest better if needed.
    """

    ai_response = ask_gemini(prompt)

    return {
        "system_choice": best,
        "ai_advice": ai_response
    }


# ---------------- DELAY ----------------
def estimate_delay(risk):
    if risk < 0.3:
        return 0
    elif risk < 0.6:
        return 2
    elif risk < 0.8:
        return 6
    else:
        return 12


# ---------------- DISRUPTION ----------------
def detect_disruption(risk, history):

    if risk > 0.75:
        return "CRITICAL"
    elif len(history) >= 2 and (history[-1]["risk"] - history[-2]["risk"] > 0.2):
        return "RISING_FAST"
    elif risk > 0.5:
        return "WARNING"
    else:
        return "SAFE"


# ---------------- ACTION ----------------
def get_action(status, weather):

    # System logic
    if status == "CRITICAL":
        system_action = "REROUTE IMMEDIATELY"
    elif status == "RISING_FAST":
        system_action = "PREPARE REROUTE"
    elif weather["wind"] > 30:
        system_action = "REDUCE SPEED"
    else:
        system_action = "NORMAL OPERATION"

    # AI Advice
    prompt = f"""
    Status: {status}
    Weather: {weather}

    System suggests: {system_action}

    Do you agree?
    """

    ai_response = ask_gemini(prompt)

    return {
        "system_action": system_action,
        "ai_advice": ai_response
    }