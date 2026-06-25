# Hello DevOps — Starter Project

A minimal but real DevOps pipeline:
Flask app → Docker → Jenkins CI/CD → Prometheus metrics → Grafana dashboard

## Prerequisites
- Docker Desktop installed (includes docker-compose)
- Git installed
- That's it

---

## Option A — Run everything with one command (easiest)

```bash
docker-compose up -d
```

This starts all four services:

| Service    | URL                        | Login         |
|------------|----------------------------|---------------|
| Flask app  | http://localhost:5000      | —             |
| Jenkins    | http://localhost:8080      | setup wizard  |
| Prometheus | http://localhost:9090      | —             |
| Grafana    | http://localhost:3000      | admin / admin |

---

## Option B — Manual step-by-step (recommended for learning)

### Step 1 — Run the Flask app directly

```bash
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000 — you should see `{"message": "Hello, World!"}`
Visit http://localhost:5000/metrics — you'll see Prometheus-formatted text

### Step 2 — Build and run with Docker

```bash
docker build -t hello-devops .
docker run -p 5000:5000 hello-devops
```

Same result, but now it runs in a container.

### Step 3 — Start Jenkins

```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

1. Open http://localhost:8080
2. Get the unlock password: `docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword`
3. Install suggested plugins
4. Create your admin user
5. Create a new Pipeline job → point it at this repo → Jenkins reads the Jenkinsfile automatically

### Step 4 — Start Prometheus

```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

Open http://localhost:9090 and search for `app_requests_total`

### Step 5 — Start Grafana

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

1. Open http://localhost:3000 (login: admin / admin)
2. Add data source → Prometheus → URL: http://host.docker.internal:9090
3. Create a dashboard panel with query: `rate(app_requests_total[1m])`

---

## Project structure

```
hello-devops/
├── app.py            ← Flask app (Hello World + /metrics + /health)
├── requirements.txt  ← Python dependencies
├── Dockerfile        ← Container recipe
├── Jenkinsfile       ← CI/CD pipeline (5 stages)
├── prometheus.yml    ← Prometheus scrape config
├── docker-compose.yml← Run everything with one command
└── README.md         ← This file
```

## What each Jenkinsfile stage does

| Stage        | What happens                                        |
|--------------|-----------------------------------------------------|
| Checkout     | Jenkins pulls your latest code from Git             |
| Build        | `docker build` — creates your image                 |
| Test         | Runs Python tests inside a throwaway container      |
| Deploy       | Stops old container, starts new one                 |
| Smoke test   | Hits `/health` to confirm the live app responds     |

---

## Next steps (when you're ready)

- **Add a GitHub webhook** so Jenkins triggers on every push (not just manually)
- **Push the Docker image to Docker Hub** after a successful build
- **Add Kubernetes** — swap the Docker run in Deploy stage for `kubectl apply`
- **Add Ansible** — use it to provision the server Jenkins deploys to
