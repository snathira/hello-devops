pipeline {

    // Run on any available Jenkins agent
    agent any

    // Variables used across stages
    environment {
        IMAGE_NAME = "hello-devops"
        IMAGE_TAG  = "build-${env.BUILD_NUMBER}"  // e.g. build-12
        CONTAINER_NAME = "hello-devops-app"
        APP_PORT = "5000"
    }

    stages {

        // --------------------------------------------------
        // Stage 1 — pull the latest code
        // --------------------------------------------------
        stage('Checkout') {
            steps {
                echo "Checking out code from branch: ${env.BRANCH_NAME}"
                checkout scm
            }
        }

        // --------------------------------------------------
        // Stage 2 — build the Docker image
        // --------------------------------------------------
        stage('Build Docker image') {
            steps {
                echo "Building image ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                // Also tag as 'latest' for convenience
                sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest"
            }
        }

        // --------------------------------------------------
        // Stage 3 — run tests inside a throwaway container
        // --------------------------------------------------
        stage('Test') {
            steps {
                echo "Running tests..."
                sh """
                    docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} \
                        python -c "
import app
client = app.app.test_client()

# Test root endpoint
r = client.get('/')
assert r.status_code == 200, f'Expected 200, got {r.status_code}'
assert b'Vanakkam' in r.data, 'Missing Hello in response'

# Test health endpoint
r = client.get('/health')
assert r.status_code == 200, 'Health check failed'

# Test metrics endpoint
r = client.get('/metrics')
assert r.status_code == 200, 'Metrics endpoint failed'
assert b'app_requests_total' in r.data, 'Metrics missing'

print('All tests passed.')
                    "
                """
            }
        }

        // --------------------------------------------------
        // Stage 4 — deploy: run the container locally
        // --------------------------------------------------
        stage('Deploy') {
            steps {
                echo "Deploying container..."

                // Stop and remove any old running container (ignore errors if none exists)
                sh "docker stop ${CONTAINER_NAME} || true"
                sh "docker rm   ${CONTAINER_NAME} || true"

                // Start the new container
                sh """
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:5000 \
                        --restart unless-stopped \
                        ${IMAGE_NAME}:${IMAGE_TAG}
                """

                // Wait a moment for the app to start
                sh "sleep 3"
            }
        }

        // --------------------------------------------------
        // Stage 5 — smoke test: hit the live container
        // --------------------------------------------------
        stage('Smoke test') {
            steps {
                echo "Smoke testing the live container..."
                sh """
                    STATUS=\$(curl -s -o /dev/null -w '%{http_code}' http://host.docker.internal:${APP_PORT}/health)
                    if [ "\$STATUS" != "200" ]; then
                        echo "Smoke test FAILED — /health returned \$STATUS"
                        exit 1
                    fi
                    echo "Smoke test passed — app is live on port ${APP_PORT}"
                """
            }
        }

    }

    // --------------------------------------------------
    // Post-pipeline actions (always run)
    // --------------------------------------------------
    post {
        success {
            echo """
            ============================================
            Build ${env.BUILD_NUMBER} SUCCEEDED
            Image : ${IMAGE_NAME}:${IMAGE_TAG}
            App   : http://localhost:${APP_PORT}
            Metrics: http://localhost:${APP_PORT}/metrics
            ============================================
            """
        }

        failure {
            echo "Build ${env.BUILD_NUMBER} FAILED — check the console output above."

            // Stop the container if the deploy or smoke test failed
            sh "docker stop ${CONTAINER_NAME} || true"
            sh "docker rm   ${CONTAINER_NAME} || true"
        }

        always {
            // Clean up old Docker images — keep the last 3 builds
            sh """
                docker images ${IMAGE_NAME} --format '{{.Tag}}' \
                | grep '^build-' \
                | sort -t- -k2 -n \
                | head -n -3 \
                | xargs -I{} docker rmi ${IMAGE_NAME}:{} || true
            """
        }
    }
}
