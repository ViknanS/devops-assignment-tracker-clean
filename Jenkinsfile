pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'python3 -m venv .venv'
                sh '. .venv/bin/activate && pip install -r backend/requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh '. .venv/bin/activate && python -m py_compile backend/app.py'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t student-assignment-tracker:latest .'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker rm -f student-assignment-tracker || true'
                sh 'docker run -d --name student-assignment-tracker -p 5005:5000 student-assignment-tracker:latest'
            }
        }
    }
}