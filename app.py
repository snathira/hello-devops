from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

# --- Prometheus metrics ---
REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)

# --- Routes ---

@app.route('/')
def hello():
    start = time.time()

    response = jsonify({
        "message": "Hello, Nathira Salim!",
        "status": "ok"
    })

    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    REQUEST_LATENCY.labels(endpoint='/').observe(time.time() - start)

    return response


@app.route('/health')
def health():
    """Health check endpoint — Jenkins uses this to verify the app started."""
    return jsonify({"status": "healthy"}), 200


@app.route('/metrics')
def metrics():
    """Prometheus scrapes this endpoint every 15 seconds."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
