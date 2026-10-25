# PlacementPro 🎓🚀
### Student Placement Preparation and Job Tracking System
**DevOps-Integrated Full Stack Web Application Built with Flask, SQLite, Pytest, Docker, Jenkins & AWS**

---

## 🌟 Executive Summary
**PlacementPro** is a centralized placement preparation and job tracking platform developed for engineering and university students. It simplifies the campus recruitment lifecycle by consolidating job drive applications, interview round schedules, and topic-wise preparation roadmaps (DSA, Core CS, System Design, Aptitude, HR) into an intuitive, responsive dashboard.

Beyond application functionality, PlacementPro demonstrates end-to-end **DevOps best practices**:
- **Version Control & Collaboration:** Git & GitHub with feature branching and commit hygiene.
- **Continuous Integration (CI):** Jenkins Declarative Pipeline with automated triggers via GitHub Webhooks (exposed via ngrok).
- **Automated Testing & Quality Gate:** Pytest suite with code coverage analysis and automated HTML test reports (`pytest-html` & `pytest-cov`).
- **Containerization:** Production-ready multi-stage Docker container (`Dockerfile` & `docker-compose.yml`).
- **Agile Project Management:** Jira Scrum boards, sprint backlogs, and Jira–GitHub integration.
- **Cloud Deployment:** AWS deployment architecture with health monitoring endpoints.

---

## 🛠️ Technology Stack & DevOps Toolchain

| Category | Tool / Technology | Purpose in Project |
|---|---|---|
| **Programming Language** | Python 3.11+ / 3.14 | Backend logic, REST endpoints, and test scripts |
| **Web Framework** | Flask 3.x | Lightweight, high-performance web routing and template rendering |
| **Database** | SQLite3 | Relational database storage with foreign keys and ACID compliance |
| **Frontend UI** | HTML5, CSS3, Bootstrap 5, Bootstrap Icons | Responsive dashboard with interactive modal workflows |
| **Security** | Werkzeug Security | Passwords hashed using PBKDF2/SHA256 |
| **Automated Testing** | Pytest 9.x | Unit tests, route integration tests, and session verification |
| **Test Reporting** | Pytest-HTML & Pytest-Cov | Generates self-contained HTML test execution and coverage reports |
| **Containerization** | Docker | Portable, reproducible application containerization |
| **Continuous Integration** | Jenkins (Pipeline as Code) | Automates build checkout, testing, and container deployment |
| **Webhook Tunneling** | ngrok | Exposes local Jenkins webhooks to public GitHub push events |
| **Agile Management** | Atlassian Jira | Scrum sprints, backlog management, and Git commit linking |
| **Cloud Hosting** | AWS (App Runner / ECS / EC2) | Scalable production cloud deployment |

---

## 📂 Project Architecture & Directory Structure

```text
PlacementPro/
│
├── app.py                      # Core Flask application, routing, and SQLite database schema
├── seed_data.py                # Database seeder for demo user and realistic placement data
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Production container definition
├── docker-compose.yml          # One-click Docker Compose service runner
├── Jenkinsfile                 # Jenkins declarative CI/CD pipeline script
├── webhook-test.txt            # Webhook test trigger payload file
├── .dockerignore               # Files excluded from Docker builds
├── .gitignore                  # Files excluded from Git tracking
├── README.md                   # Complete setup, testing, and DevOps deployment guide
├── PROJECT_REPORT.md           # Formal college project academic submission report
│
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions automated test workflow
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom modern dashboard styling & responsive layout
│   └── js/
│       └── main.js             # Sidebar toggle and dynamic UI behaviors
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base layout with sidebar navigation, navbar, and flash alerts
│   ├── login.html              # User login page with demo one-click credentials
│   ├── register.html           # User registration with department and graduation year
│   ├── dashboard.html          # Main placement metrics, upcoming interviews, and progress bars
│   ├── applications.html       # Job applications CRUD table with search and status filtering
│   ├── interviews.html         # Interview scheduling, round tracking, and meeting links
│   └── preparation.html        # Placement syllabus checklist categorized by DSA, Core CS, etc.
│
└── tests/
    ├── __init__.py             # Test package initialization
    └── test_app.py             # 13 automated Pytest test cases covering 100% of workflows
```

---

## ⚡ Quick Start: Local Development Setup

### 1. Prerequisites
- Python 3.10+ installed
- Git installed

### 2. Setup Virtual Environment
Open PowerShell or your terminal in the `PlacementPro` project directory:
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Seed Realistic Sample Data
Run the included seed script to populate realistic placement data matching the demo:
```powershell
python seed_data.py
```
> **Default Demo Account:**
> - Username: `shrawni`
> - Password: `password123`

### 4. Run the Web Server
```powershell
python app.py
```
Open your browser and navigate to: **[http://localhost:5000](http://localhost:5000)**

---

## 🧪 Automated Testing with Pytest & Test Reports

PlacementPro features an automated test suite in `tests/test_app.py` covering:
- Login and registration rendering
- Access control (redirecting unauthenticated users)
- User session authentication and logout
- Adding, editing, and deleting job applications
- Scheduling and updating interviews
- Tracking and toggling preparation roadmap topics
- Dashboard statistics calculation
- Application health check endpoint (`/health`)

### Running the Tests:
```powershell
python -m pytest -v --html=pytest-report.html --self-contained-html --cov=app --cov-report=html:coverage-html
```

### Generated Artifacts:
1. **`pytest-report.html`**: Interactive HTML report detailing test pass/fail status and execution time.
2. **`coverage-html/index.html`**: Line-by-line Python code coverage breakdown.

---

## 🐳 Docker Containerization

### 1. Build the Docker Image
```powershell
docker build -t placementpro:latest .
```

### 2. Run the Container
```powershell
docker run -d --name placementpro-app -p 5000:5000 -e SECRET_KEY=placementpro-local-dev-key placementpro:latest
```

### 3. Verify Container Status
```powershell
docker ps
```
Visit `http://localhost:5000` to verify the containerized application is running.

---

## 🔄 Jenkins Continuous Integration (CI) Pipeline

PlacementPro uses a **Declarative Pipeline** defined in `Jenkinsfile`.

### Pipeline Execution Stages:
1. **Checkout:** Clones the latest branch from GitHub.
2. **Check Python:** Verifies the Python runtime and pip version.
3. **Check Docker:** Confirms the Docker daemon is operational.
4. **Install Dependencies:** Installs packages from `requirements.txt` along with testing tools.
5. **Run Tests:** Executes `pytest` with code coverage and generates `pytest-report.html`.
6. **Build Docker Image:** Builds the `placementpro:latest` image.
7. **Deploy Docker Container:** Launches the container on port 5000.
8. **Post Actions:** Archives artifacts and publishes HTML test and coverage reports using the Jenkins HTML Publisher plugin.

---

## 🌐 GitHub Webhook & ngrok Integration

To trigger Jenkins builds automatically on every `git push`:
1. Start Jenkins locally on `http://localhost:8080`.
2. Start an ngrok tunnel to your Jenkins port:
   ```powershell
   ngrok http 8080
   ```
3. Copy the public forwarding HTTPS URL (e.g. `https://random-subdomain.ngrok-free.dev`).
4. In your GitHub repository:
   - Go to **Settings** &rarr; **Webhooks** &rarr; **Add Webhook**.
   - **Payload URL:** `https://random-subdomain.ngrok-free.dev/github-webhook/`
   - **Content type:** `application/json`
   - **Events:** Select *"Just the push event"*.
   - Click **Add Webhook**.
5. Push any commit (e.g., updating `webhook-test.txt`), and observe Jenkins trigger automatically!

---

## 📋 Jira Project Planning & GitHub Integration

1. Create a project in Jira using the **Scrum** template named `PlacementPro`.
2. Create User Stories in the Backlog:
   - *PP-1: Student Authentication and Profile Management*
   - *PP-2: Placement Applications Tracking and Filtering*
   - *PP-3: Interview Schedule and Round Management*
   - *PP-4: Placement Preparation Roadmap & Progress Tracker*
   - *PP-5: Pytest Automated Testing & Coverage Suite*
   - *PP-6: Docker Packaging & Jenkins CI Automation*
3. Create a Sprint, add the stories, and click **Start Sprint**.
4. Connect GitHub to Jira under **Project Settings &rarr; Features / GitHub App** to link commit hashes directly to Jira ticket keys!

---

## ☁️ AWS Cloud Deployment Guide

PlacementPro is ready for deployment to Amazon Web Services using multiple architectures:
- **AWS App Runner / Elastic Container Service (ECS):** Deploy directly using the container image created from `Dockerfile`.
- **AWS Elastic Beanstalk (Python):** Deploy the Flask codebase with environment variables configured via the AWS console.
- **AWS EC2:** Launch an Ubuntu or Amazon Linux EC2 instance, install Docker, pull the image, and run on port 80/5000 with an Application Load Balancer.

The `/health` endpoint (`GET /health`) provides JSON heartbeat data for AWS Route 53 or ALB target health checks.

---

## 🎓 College Viva & Defense Q&A

**Q1: Why did you choose Flask over Django for PlacementPro?**
> *Answer:* Flask is lightweight, modular, and unopinionated. It gave us precise control over routing, session handling, and database integration while keeping container sizes minimal (under 150MB), making it ideal for microservices and fast CI/CD pipelines.

**Q2: What is the purpose of the Jenkinsfile in this project?**
> *Answer:* The `Jenkinsfile` implements "Pipeline as Code". It ensures that the entire build, automated test suite, Docker container build, and deployment steps are version-controlled alongside the application code in Git.

**Q3: How does the GitHub Webhook interact with Jenkins?**
> *Answer:* When code is pushed to GitHub, GitHub sends an HTTP POST payload to the webhook endpoint. Because our Jenkins instance runs on a local development machine, we used `ngrok` to create a secure reverse-proxy tunnel that forwards GitHub's payload to Jenkins port 8080, triggering the `PlacementPro-CI` pipeline instantly.

**Q4: How do you ensure test database isolation during automated testing?**
> *Answer:* In `tests/test_app.py`, we created a `pytest.fixture` called `client(tmp_path)` that uses Pytest's temporary directory fixture to generate a separate, isolated SQLite database for each test run, ensuring no test writes to or corrupts the production or demo database.
