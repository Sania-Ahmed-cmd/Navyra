# optimization.py

# ---------------- ROUTES (SHIP-BASED) ----------------
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
    ],

    "Serene": [
        {"name": "Mediterranean Path", "weather_sensitivity": 0.5, "congestion": 0.8, "distance": 1.0},
        {"name": "Open Sea Route", "weather_sensitivity": 0.7, "congestion": 0.4, "distance": 1.1}
    ],

    "Dubai": [
        {"name": "Gulf Corridor", "weather_sensitivity": 0.6, "congestion": 0.9, "distance": 1.0},
        {"name": "Indian Ocean Route", "weather_sensitivity": 0.8, "congestion": 0.4, "distance": 1.2}
    ],

    "Al Said": [
        {"name": "Arabian Route", "weather_sensitivity": 0.7, "congestion": 0.6, "distance": 1.0},
        {"name": "Deep Ocean Path", "weather_sensitivity": 0.9, "congestion": 0.3, "distance": 1.2}
    ],

    "Radiant": [
        {"name": "Northern Trade Route", "weather_sensitivity": 0.8, "congestion": 0.5, "distance": 1.0},
        {"name": "Low Risk Detour", "weather_sensitivity": 0.4, "congestion": 0.3, "distance": 1.3}
    ],

    "Octopus": [
        {"name": "Research Corridor", "weather_sensitivity": 0.6, "congestion": 0.2, "distance": 1.1},
        {"name": "Storm Avoidance Route", "weather_sensitivity": 0.3, "congestion": 0.3, "distance": 1.4}
    ],

    "Lady Moura": [
        {"name": "Luxury Coastal Route", "weather_sensitivity": 0.5, "congestion": 0.7, "distance": 1.0},
        {"name": "Balanced Ocean Route", "weather_sensitivity": 0.6, "congestion": 0.5, "distance": 1.1}
    ],

    "Nord": [
        {"name": "Northern Ice Edge", "weather_sensitivity": 1.2, "congestion": 0.2, "distance": 0.9},
        {"name": "Safe Southern Loop", "weather_sensitivity": 0.5, "congestion": 0.3, "distance": 1.4}
    ]
}


# ---------------- WEATHER EXPOSURE ----------------
def compute_weather_exposure(wind, sensitivity):
    return min((wind / 40) * sensitivity, 1)


# ---------------- ROUTE OPTIMIZATION ----------------
def choose_best_route(base_risk, ship_name, wind):

    if ship_name not in routes:
        return "DEFAULT ROUTE"

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

    return best


# ---------------- DELAY ----------------
def estimate_delay(risk):

    if risk < 0.3:
        return 0
    if risk < 0.6:
        return 2
    if risk < 0.8:
        return 6
    return 12


# ---------------- DISRUPTION ----------------
def detect_disruption(risk, history):

    if risk > 0.75:
        return "CRITICAL"

    if len(history) >= 2:
        if history[-1]["risk"] - history[-2]["risk"] > 0.2:
            return "RISING_FAST"

    if risk > 0.5:
        return "WARNING"

    return "SAFE"


# ---------------- ACTION ----------------
def get_action(status, weather):

    if status == "CRITICAL":
        return "REROUTE IMMEDIATELY"

    if status == "RISING_FAST":
        return "PREPARE REROUTE"

    if weather["wind"] > 30:
        return "REDUCE SPEED"

    return "NORMAL OPERATION"