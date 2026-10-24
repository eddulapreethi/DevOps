pipeline {
    agent any

    stages {
        stage('Install Dependencies and Run Tests') {
            steps {
                echo 'Installing dependencies and running Recipe Organizer tests'
                bat 'pip install -r requirements.txt'
                bat 'python -m pip install pytest'
                bat 'python -m pytest -v tests'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Recipe Organizer Docker image'
                bat 'cd CaseStudy && docker build -t recipe-organizer:build .'
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    bat 'echo %DOCKERHUB_TOKEN%| docker login -u %DOCKERHUB_USERNAME% --password-stdin'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    bat 'docker tag recipe-organizer:build eddulapreethi/simple_demo:%BUILD_NUMBER%'
                    bat 'docker tag recipe-organizer:build eddulapreethi/simple_demo:latest'
                    bat 'docker push eddulapreethi/simple_demo:%BUILD_NUMBER%'
                    bat 'docker push eddulapreethi/simple_demo:latest'
                    bat 'docker logout'
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    bat 'cd CaseStudy && kubectl apply -f deployment.yaml --validate=false'
                    bat 'cd CaseStudy && kubectl apply -f service.yaml'
                    bat 'kubectl set image deployment/recipe-organizer recipe-organizer=eddulapreethi/simple_demo:%BUILD_NUMBER%'
                    bat 'kubectl rollout status deployment/recipe-organizer --timeout=120s'
                }
            }
        }
    }

    post {
        success {
            echo 'Recipe Organizer pipeline completed successfully!'
        }
        failure {
            echo 'Recipe Organizer pipeline failed. Please check the logs.'
        }
    }
}
