# Manual de Instalación y Ejecución – Risk Alerts Provisorio

Este script automatiza el monitoreo de riesgo de una lista fija de RUTs de proveedores.

---

## 📋 ¿Qué hace este script?

- Crea validaciones para RUTs definidos en el código.
- Consulta Watchlist, Legal Cases y Actividades Económicas.
- Calcula un `Risk Score` por proveedor.
- Genera un CSV con resultados diarios.
- Envía alerta a Slack si el riesgo ≥ 80.
- Deja un log de cada ejecución.

---

## ⚙️ Instalación y Ejecución Local

### Requisitos:
- Python 3.8 o superior
- pip

### Pasos:

```bash
# 1. Clonar o descargar el proyecto
cd risk-alerts-project

# 2. Crear entorno virtual (opcional)
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
export PLUTTO_API_KEY="sk_..."
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."  # opcional para crear alerta de slack, falta este paso

# 5. Ejecutar proceso
python risk_alerts.py


# El Risk Score se calcula por proveedor en base a:


Fuente	Condición	Puntos
Watchlist	Si aparece en alguna lista	+50
Legal Cases	Si tiene casos legales asociados	+30
Actividad Económica	Si corresponde a rubros de riesgo	+20
Total máximo: 100 puntos.

Alerta: Si el score es igual o mayor a 80, se dispara una alerta en Slack.
Actividades económicas consideradas de riesgo incluyen, por ejemplo: casinos, construcción, etc. (códigos como 921910, 411010, 410000)