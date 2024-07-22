pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "fake_calls_detection"
        JAVA_OPTS = '-Dfile.encoding=UTF-8'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/Kowallskiy/jenkins', branch: 'main'
            }
        }
        stage('Verify the Environment') {
            steps {
                echo 'Start verifying...'
                bat 'chcp 65001'  // Set code page to UTF-8 for Windows
                bat 'C:/Users/user/AppData/Local/Programs/Python/Python312/python.exe --version'
                bat 'C:/Users/user/AppData/Local/Programs/Python/Python312/Scripts/pip --version'
                // bat 'pytest --version'
                echo 'Finished verifying.'
            }
        }
        // stage('Install Dependencies') {
        //     steps {
        //         bat 'pip install -r requirements.txt'
        //     }
        // }
        stage('Run Tests') {
            steps {
                echo 'Testing...'
                bat 'C:/Users/user/AppData/Local/Programs/Python/Python312/Lib/site-packages/pytest C:/Users/user/Desktop/audio/app/test'
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
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                    bat 'echo %DOCKERHUB_PASSWORD% | docker login -u %DOCKERHUB_USERNAME% --password-stdin'
                }
                script {
                    docker.image(DOCKER_IMAGE).push()
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to Kubernetes...'
                // Add Kubernetes deployment steps here
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}

