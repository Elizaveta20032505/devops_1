// CI: pytest → Docker build + push (PR в main). Агент: Docker CLI + Python 3 (venv .ci-venv).
// Jenkins: Multibranch Pipeline + GitHub.
// Credential dockerhub-creds (username + Access Token с hub.docker.com).

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
        // Jenkins → Manage Jenkins → Global properties → Environment variables: DOCKERHUB_USER=yourlogin
        DOCKERHUB_USER = "${env.DOCKERHUB_USER ?: 'YOUR_DOCKERHUB_LOGIN'}"
        IMAGE = "${DOCKERHUB_USER}/devops1-api"
        TAG = "pr-${env.CHANGE_ID ?: '0'}-${env.BUILD_NUMBER}"
    }

    stages {
        stage('info') {
            steps {
                echo "CHANGE_ID=${env.CHANGE_ID} CHANGE_TARGET=${env.CHANGE_TARGET} BRANCH=${env.BRANCH_NAME}"
            }
        }

        stage('checkout') {
            when {
                expression { env.CHANGE_ID != null && env.CHANGE_TARGET == 'main' }
            }
            steps {
                checkout scm
            }
        }

        stage('pytest') {
            when {
                expression { env.CHANGE_ID != null && env.CHANGE_TARGET == 'main' }
            }
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            set -e
                            python -m venv .ci-venv
                            . .ci-venv/bin/activate
                            pip install -q -r requirements.txt
                            pytest -q
                        '''
                    } else {
                        bat '''
                            python -m venv .ci-venv
                            call .ci-venv/Scripts/activate.bat
                            python -m pip install -q -r requirements.txt
                            python -m pytest -q
                        '''
                    }
                }
            }
        }

        stage('docker_build') {
            when {
                expression { env.CHANGE_ID != null && env.CHANGE_TARGET == 'main' }
            }
            steps {
                script {
                    if (isUnix()) {
                        sh 'docker --version'
                        sh "docker build -t ${IMAGE}:${TAG} ."
                    } else {
                        bat 'docker --version'
                        bat "docker build -t ${IMAGE}:${TAG} ."
                    }
                }
            }
        }

        stage('docker_push') {
            when {
                expression { env.CHANGE_ID != null && env.CHANGE_TARGET == 'main' }
            }
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_PASS'
                    )
                ]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                set -e
                                echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                            '''
                            sh "docker push ${IMAGE}:${TAG}"
                        } else {
                            // Windows: нет sh; пароль не подставляем в строку Groovy — только env в cmd.
                            bat 'echo %DH_PASS%| docker login -u %DH_USER% --password-stdin'
                            bat "docker push ${IMAGE}:${TAG}"
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                if (env.CHANGE_ID != null && env.CHANGE_TARGET == 'main') {
                    // П.10: CD job в Jenkins должен называться так же (или поменяй имя здесь и в README).
                    build job: 'devops1-model-cd', parameters: [string(name: 'IMAGE_TAG', value: "${env.TAG}")], wait: false
                }
            }
        }
        failure {
            echo 'Проверь: pytest (стадия pytest), dockerhub-creds, DOCKERHUB_USER, логи docker push.'
        }
    }
}
