pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "fake_calls_detection"
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/Kowallskiy/jenkins', branch: 'main'
            }
        }
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
                echo 'Testing...'
                sh 'pytest app/tests/test_main.py'
            }
        }
        stage('Build Docker Image') {
            steps {
                echo 'Building docker image...'
                script {
                    docker.build(DOCKER_IMAGE)
                }
            }
        }
        stage('Push Docker Image') {
            withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                sh 'echo $DOCKERHUB_PASSWORD | docker login -u $DOCKERHUB_USERNAME --password-stdin'
            }
            script {
                docker.image(DOCKER_IMAGE).push()
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to Kubernetes...'
            }
        }
    }
}

post {
    always {
        cleanWs()
    }
    success {
        echo 'Pipline completed successfully!'
    }
    failure {
        echo 'Pipeline failed!'
    }
}
