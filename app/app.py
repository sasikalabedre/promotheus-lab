from flask import Flask, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import random
import time

app = Flask(__name__)
REQUESTS = Counter("http_requests_total", "Total requests", ["status"])
LATENCY = Histogram("http_request_duration_seconds", "Request time in seconds", buckets=[0.05, 0.1, 0.25, 0.5, 1, 2])

@app.route("/")
def home():
    start = time.time()
    time.sleep(random.choice([0.05, 0.05, 0.05, 0.1, 0.1, 0.3, 1.5]))
    if random.random() < 0.1:
        status = "500"
    else:
        status = "200"
    REQUESTS.labels(status=status).inc()
    LATENCY.observe(time.time() - start)
    if status == "500":
        return "error", 500
    return "ok", 200

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

app.run(host="0.0.0.0", port=8080)
