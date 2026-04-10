# Student Assignment Tracker - DevOps Project

Modern Flask + SQLite assignment tracker with Docker, Jenkins pipeline, Kubernetes manifests, and Ansible deployment automation.

## Folder structure

- `backend/` - Flask app and Python dependencies
- `frontend/` - HTML templates and static assets
- `devops/` - Kubernetes and Ansible files
  - `devops/k8s/` - deployment and service manifests
  - `devops/ansible/` - playbook for Docker-based deployment

## Local run (without Docker)

1. Create virtual environment:
   - `python3 -m venv .venv`
2. Activate it:
   - `source .venv/bin/activate`
3. Install dependencies:
   - `pip install -r backend/requirements.txt`
4. Start app:
   - `python backend/app.py`
5. Open browser:
   - `http://127.0.0.1:5000`

## Docker - step by step

1. Go to project folder:
   - `cd /Users/viknans/Desktop/devops-assignment-tracker`
2. Build Docker image:
   - `docker build -t student-assignment-tracker:latest .`
3. Run container:
   - `docker run -d --name student-assignment-tracker -p 5000:5000 student-assignment-tracker:latest`
4. Check running container:
   - `docker ps`
5. Open app:
   - `http://localhost:5000`
6. Stop container when needed:
   - `docker stop student-assignment-tracker`
7. Remove container when needed:
   - `docker rm student-assignment-tracker`

## Jenkins pipeline

`Jenkinsfile` includes stages:
- Build - create venv and install dependencies
- Test - compile-check `backend/app.py`
- Docker Build - build image
- Deploy - run container on port `5000`

## Kubernetes - step by step

1. Build image:
   - `docker build -t student-assignment-tracker:latest .`
2. If using Minikube, load image into cluster:
   - `minikube image load student-assignment-tracker:latest`
3. Apply deployment:
   - `kubectl apply -f devops/k8s/deployment.yaml`
4. Apply service:
   - `kubectl apply -f devops/k8s/service.yaml`
5. Check pods:
   - `kubectl get pods`
6. Check service:
   - `kubectl get svc assignment-tracker-service`
7. Access app:
   - On Minikube: `minikube service assignment-tracker-service --url`
   - On a node: `http://<node-ip>:30080`

## Ansible - step by step

1. Install collection used by playbook:
   - `ansible-galaxy collection install community.docker`
2. Create inventory file (example `inventory.ini`):
   - `[app]`
   - `your-server-ip ansible_user=ubuntu`
3. Run playbook:
   - `ansible-playbook -i inventory.ini devops/ansible/ansible-playbook.yml`

What this playbook does in simple words:
- Installs Docker
- Starts Docker service
- Pulls app image
- Runs app container on port `5000`
