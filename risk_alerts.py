
import requests
import pandas as pd
import os
import logging
from datetime import datetime

API_KEY = os.getenv("PLUTTO_API_KEY")
BASE_URL = "https://kyb-staging.getplutto.com"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

HIGH_RISK_ACTIVITIES = {"921910", "411010", "410000"}
RUTS_A_MONITOREAR = ["96967960-4", "78451050-6"]

fecha = datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(
    filename=f"log_{fecha}.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def crear_validacion(rut):
    try:
        res = requests.post(f"{BASE_URL}/v1/validations", headers=HEADERS, json={"tax_id": rut})
        res.raise_for_status()
        return res.json().get("data")
    except Exception as e:
        logging.error(f"Error creando validación para RUT {rut}: {e}")
        return None

def fetch_validation_details(validation_id):
    try:
        wl_url = f"{BASE_URL}/v1/validations/{validation_id}/watchlists"
        lc_url = f"{BASE_URL}/v1/validations/{validation_id}/legal-cases"
        wl = requests.get(wl_url, headers=HEADERS).json().get("data", [])
        lc = requests.get(lc_url, headers=HEADERS).json().get("data", [])
        return wl, lc
    except Exception as e:
        logging.warning(f"Error al obtener detalles para validación {validation_id}: {e}")
        return [], []

def calculate_score(validation):
    score = 0
    validation_id = validation.get("id")

    if validation_id:
        watchlists, legal_cases = fetch_validation_details(validation_id)
        if watchlists:
            score += 50
        if legal_cases:
            score += 30

    activities = validation.get("entity", {}).get("tax_office_data", {}).get("activities", [])
    for act in activities:
        if act.get("code") in HIGH_RISK_ACTIVITIES:
            score += 20
            break

    return min(score, 100)

def send_slack_alert(supplier_id, score):
    if not SLACK_WEBHOOK_URL:
        return
    payload = {
        "text": f"🚨 *Alerta de Riesgo*\nProveedor `{supplier_id}` tiene un Risk Score de `{score}`."
    }
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if resp.status_code != 200:
            raise ValueError(f"Slack error: {resp.text}")
        logging.info(f"Alerta enviada para {supplier_id} con score {score}")
    except Exception as e:
        logging.error(f"Error enviando alerta Slack: {e}")

def main():
    timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    output = []

    for rut in RUTS_A_MONITOREAR:
        validacion = crear_validacion(rut)
        if not validacion:
            continue

        supplier_id = validacion.get("entity", {}).get("id", rut)
        score = calculate_score(validacion)
        output.append({
            "supplier_id": supplier_id,
            "computed_risk_score": score,
            "timestamp": timestamp
        })

        if score >= 80:
            send_slack_alert(supplier_id, score)

    df = pd.DataFrame(output)
    csv_name = f"risk_report_{fecha}.csv"
    df.to_csv(csv_name, index=False)
    logging.info(f"Proceso completado. Se generó {csv_name}")

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        logging.error(f"Error crítico: {err}")
