pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Syntax Check') {
            steps {
                sh 'python3 -m compileall backend layers/shared -q'
            }
        }

        stage('Validate Template') {
            steps {
                sh 'sam validate'
            }
        }

        stage('Build') {
            steps {
                sh 'sam build'
            }
        }
    }

    post {
        success { echo 'CI GREEN: template valid, all Lambda code compiles, SAM build passed' }
        failure { echo 'CI RED: inspect the failed stage above' }
    }
}