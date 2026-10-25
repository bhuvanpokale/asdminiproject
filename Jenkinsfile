pipeline {
    agent any

    environment {
        SECRET_KEY = 'placementpro-local-dev-key'
        PORT = '5000'
        IMAGE_NAME = 'placementpro'
        CONTAINER_NAME = 'placementpro-app'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out latest source code from GitHub repository...'
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                echo 'Verifying Python runtime and package manager...'
                bat 'python --version'
                bat 'python -m pip --version'
            }
        }

        stage('Check Docker') {
            steps {
                echo 'Verifying Docker installation...'
                bat 'docker --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing application and testing dependencies...'
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install -r requirements.txt'
                bat 'python -m pip install pytest pytest-html pytest-cov'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Executing automated test suite with Pytest and generating HTML reports...'
                bat 'python -m pytest -v --html=pytest-report.html --self-contained-html --cov=app --cov-report=html:coverage-html'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building containerized application Docker image...'
                bat "docker build -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Deploy Docker Container') {
            steps {
                echo 'Deploying PlacementPro container...'
                bat """
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p 5000:5000 -e SECRET_KEY=${SECRET_KEY} ${IMAGE_NAME}:latest
                """
            }
        }
    }

    post {
        always {
            echo 'Archiving test and coverage artifacts...'
            archiveArtifacts artifacts: 'pytest-report.html, coverage-html/**/*', allowEmptyArchive: true

            // Publish Pytest HTML Report
            publishHTML(target: [
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'pytest-report.html',
                reportName: 'PlacementPro Test Report',
                reportTitles: 'PlacementPro Automated Pytest Results'
            ])

            // Publish Pytest Code Coverage Report
            publishHTML(target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'coverage-html',
                reportFiles: 'index.html',
                reportName: 'PlacementPro Coverage Report',
                reportTitles: 'PlacementPro Python Code Coverage'
            ])
        }
        success {
            echo 'PlacementPro CI/CD pipeline completed successfully!'
        }
        failure {
            echo 'PlacementPro pipeline build failed. Please inspect test or container logs.'
        }
    }
}
