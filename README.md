# Prometheus Lab

Monitoring practice with Prometheus, Node Exporter and Grafana, running in Docker on an Ubuntu laptop.

## Study notes

1. **Metrics, logs, traces:** metrics are numbers over time (alerts, trends), logs are text records of events (the reason for an error), traces follow one request across services (where it is slow).
2. **Prometheus basics:** it scrapes (pulls) `/metrics` from targets. Exporters expose metrics for systems. Labels are tags. One metric plus one label set is one time series. TSDB is its built-in database.
3. **PromQL and metric types:** counter (only goes up, use `rate()`), gauge (up and down), histogram (buckets, percentiles with `histogram_quantile`), summary (percentiles calculated by the app).
4. **Node Exporter and instrumentation:** Node Exporter gives server metrics. Client libraries in app code give application metrics.
5. **Grafana:** dashboards and panels, variables (dropdowns), transformations (change data after query), alert rules.
6. **Recording rules, cardinality, retention:** recording rules save heavy queries as new metrics. High cardinality (many label values) hurts memory. Default retention is 15 days.
7. **RED and USE:** RED (Rate, Errors, Duration) for services. USE (Utilization, Saturation, Errors) for resources.

## Reliability theory

1. **SLI, SLO, SLA, error budget:** SLI is what you measure, SLO is the goal, SLA is the promise to customers, error budget is 100% minus SLO (99.9% over 30 days is 43.2 minutes).
2. **Availability, latency, throughput, error rate:** the four common SLIs. Use p95/p99 for latency, not the average.
3. **Multi-window, multi-burn-rate alerting:** burn rate is how fast the error budget is used (actual error rate / allowed error rate). Fast burn pages, slow burn makes a ticket. A long window confirms the problem is real, a short window confirms it is still happening.
4. **Golden signals and actionable alerts:** latency, traffic, errors, saturation. Alert on symptoms, give every alert an action, use a pending period, add a runbook link.

## Setup

```bash
# Node Exporter
docker run -d --name node-exporter -p 9100:9100 --pid=host -v /:/host:ro,rslave prom/node-exporter --path.rootfs=/host

# Prometheus (port 9091 because 9090 is used by MinIO)
docker run -d --name prometheus -p 9091:9090 --add-host=host.docker.internal:host-gateway -v ~/prometheus-lab/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus

# Grafana
docker run -d --name grafana-lab -p 3000:3000 --add-host=host.docker.internal:host-gateway grafana/grafana:11.2.0
```

Grafana data source URL: `http://host.docker.internal:9091`

## Hands-on tasks

1. **Deploy Prometheus and Node Exporter:** done, target `node` is UP.
2. **Add an Ubuntu host as a scrape target:** added `ubuntu-host` job with custom labels `env=lab`, `os=ubuntu` in `prometheus.yml`.
3. **Dashboards:** CPU, memory, disk and network panels in Grafana.
4. **PromQL queries:**

```
# CPU used %
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory used %
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Memory available in GB
node_memory_MemAvailable_bytes / 1024 / 1024 / 1024

# Disk used %
100 - (node_filesystem_avail_bytes{mountpoint="/",fstype!="tmpfs"} / node_filesystem_size_bytes{mountpoint="/",fstype!="tmpfs"} * 100)

# Network download and upload (bytes per second)
rate(node_network_receive_bytes_total{device!~"lo|docker.*|veth.*|br-.*"}[5m])
rate(node_network_transmit_bytes_total{device!~"lo|docker.*|veth.*|br-.*"}[5m])
```

5. **Disk alert:** Grafana alert rule, Reduce `Last`, Threshold `IS ABOVE 85`, evaluation every 1m, pending period 1m. State goes Normal, Pending, Firing.
6. **Failed scrape target:** stopped Node Exporter with `docker stop node-exporter`. Targets page showed DOWN with `connection refused`, and `up` became `0`. Diagnosed with `docker ps` and `curl`, fixed with `docker start node-exporter`.

## Next

Practical monitoring topics: application error rate, request latency, instance availability, disk usage, pod restarts, missing data, alert rules, correlating metrics and logs.
