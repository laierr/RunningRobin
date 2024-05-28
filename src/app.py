from flask import Flask, jsonify, url_for
import os
import requests
import prometheus_client
from prometheus_client import Counter, generate_latest

app = Flask(__name__)

REQUEST_COUNT = Counter('app_request_count', 'Total number of requests sent')
AGGREGATE_COUNT = Counter('app_aggregate_count', 'Total number of aggregated responses')

REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '5'))
TARGET_URL = os.getenv("TARGET_URL", "")


@app.route('/send_request')
def send_request():
    REQUEST_COUNT.inc()
    response_data = {}
    try:
        # Try to use the primary TARGET_URL
        if TARGET_URL:
            response = requests.get(TARGET_URL, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response_data = response.json()
        else:
            # Fallback to the dummy target if TARGET_URL is not set
            fallback_url = url_for('dummy_target', _external=True)
            response = requests.get(fallback_url)
            response.raise_for_status()
            response_data = response.json()
    except Exception as e:
        # If the primary request fails, fallback to the dummy target
        try:
            fallback_url = url_for('dummy_target', _external=True)
            response = requests.get(fallback_url)
            response.raise_for_status()
            response_data = response.json()
        except Exception as fallback_error:
            return jsonify({'error': f"Primary request failed with error: {e}. Fallback also failed with error: {fallback_error}"}), 500
    
    AGGREGATE_COUNT.inc(len(response_data))
    return jsonify(response_data)

@app.route('/dummy_target')
def dummy_target():
    dummy_response = {"message": "This is a dummy response."}
    return jsonify(dummy_response)

@app.route('/metrics')
def metrics():
    return generate_latest(prometheus_client.REGISTRY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)