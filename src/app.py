from flask import Flask, jsonify, request, render_template_string
import requests
import os
import threading
import time
import logging
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST


app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ROLE = os.getenv('ROLE', 'service_a')  # Default to 'service_a'
TARGET_URL = os.getenv('TARGET_URL', 'http://localhost:5001/health_check')  
REQUEST_INTERVAL = int(os.getenv('REQUEST_INTERVAL', '10'))

# Prometheus metrics
REQUESTS_SENT = Counter(f'{ROLE}_requests_sent', 'Total number of requests sent')
RESPONSES_RECEIVED = Counter(f'{ROLE}_responses_received', 'Total number of responses received')
ERRORS = Counter(f'{ROLE}_errors', 'Total number of errors')

# Prometheus metrics endpoint
@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Human-friendly metrics view
@app.route('/metrics_view', methods=['GET'])
def metrics_view():
    metrics_html = f"""
    <html>
        <head><title>Metrics</title></head>
        <body>
            <h1>Metrics for {ROLE}</h1>
            <ul>
                <li>Total Requests Sent: {REQUESTS_SENT._value.get()}</li>
                <li>Total Responses Received: {RESPONSES_RECEIVED._value.get()}</li>
                <li>Total Errors: {ERRORS._value.get()}</li>
            </ul>
        </body>
    </html>
    """
    return render_template_string(metrics_html)

# Endpoint to return health check data
@app.route('/health_check', methods=['GET'])
def health_check():
    health_data = {
        "service": ROLE,
        "status": "healthy",
        "timestamp": time.time()
    }
    return jsonify(health_data)

# Function to send periodic requests
def periodic_request():
    time.sleep(10)
    logger.debug("[=======>PERIODIC REQUEST HAS RISEN <======]")
    while True:
        try:
            logger.debug(f"Sending request to {TARGET_URL}")
            REQUESTS_SENT.inc()
            response = requests.get(TARGET_URL, timeout=5)
            response.raise_for_status()
            RESPONSES_RECEIVED.inc()
            logger.debug(f"Received response: {response.json()}")
        except requests.RequestException as e:
            ERRORS.inc()
            logger.error(f"Request failed: {e}")
        time.sleep(REQUEST_INTERVAL)

if __name__ == '__main__':

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        logger.debug("Starting periodic request thread")
        thread = threading.Thread(target=periodic_request)
        thread.daemon = True
        thread.start()

    port=int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0',  port=port, debug=True)
