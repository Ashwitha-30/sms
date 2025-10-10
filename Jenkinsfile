pipeline {
    agent any

    environment {
        IMAGE_NAME = 'sms-app'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Ashwitha-30/sms.git'
            }
        }

        stage('Get Commit Hash') {
            steps {
                script {
                    COMMIT_HASH = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    env.IMAGE_TAG = "${COMMIT_HASH}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('Deploy') {
            steps {
                // Use secret .env file from Jenkins credentials
                withCredentials([file(credentialsId: 'sms-env-file', variable: 'ENV_FILE')]) {
                    sh """
                    docker stop ${IMAGE_NAME} || true
                    docker rm ${IMAGE_NAME} || true
                    docker run --env-file $ENV_FILE -d --name ${IMAGE_NAME} -p 5000:5000 ${IMAGE_NAME}:${IMAGE_TAG}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful! Running image tag: ${IMAGE_TAG}"
        }
        failure {
            echo "❌ Deployment failed."
        }
    }
}
