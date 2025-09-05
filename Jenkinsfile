pipeline {
  agent any

  environment {
    REPO_URL    = 'https://github.com/arielhalevy123/nice-devsecops.git'

    // שרת האפליקציה (EC2)
    REMOTE_HOST = '34.207.115.202'
    REMOTE_USER = 'ubuntu'

    // שמות ה-Credentials ב-Jenkins
    SSH_CRED_ID = 'ssh-ec2-app'              // SSH private key לשרת האפליקציה
    AWS_CRED_ID = 'aws-jenkins-devsecops'    // AWS AccessKey + Secret

    IMAGE_NAME  = 'miluim-grant:latest'
    BUCKET      = 'devsecops-scan-reports-ariel'
    AWS_REGION  = 'us-east-1'
  }

  triggers {
    githubPush()
  }

  stages {

    stage('Checkout') {
      steps { git url: env.REPO_URL, branch: 'main' }
    }

    stage('Provision Infra (OpenTofu)') {
      steps {
        withCredentials([aws(credentialsId: env.AWS_CRED_ID,
                             accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                             secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {
          sh '''
            set -e
            if [ -d infra ]; then
              cd infra
              if command -v tofu >/dev/null 2>&1; then
                tofu init -upgrade
                tofu plan -out=tfplan
                tofu apply -auto-approve tfplan
              else
                echo "NOTE: OpenTofu is not installed on this Jenkins agent - skipping infra."
              fi
            else
              echo "No infra/ directory - skipping infra."
            fi
          '''
        }
      }
    }

    stage('Build & Trivy on App Server') {
      steps {
        sshagent (credentials: [env.SSH_CRED_ID]) {
          // אין כאן withCredentials של AWS בכוונה: לא מעלים ל-S3 בשלב הזה
          sh '''
            set -e
            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -s <<'EOSH'
              set -e

              if [ -d ~/nice-devsecops ]; then
                cd ~/nice-devsecops && git pull origin main
              else
                git clone '"$REPO_URL"' ~/nice-devsecops
              fi
              cd ~/nice-devsecops/app

              docker stop miluim-grant || true
              docker rm   miluim-grant || true

              docker build -t '"$IMAGE_NAME"' .

              docker run --rm \
                -v /var/run/docker.sock:/var/run/docker.sock \
                -v "$(pwd)":/work aquasec/trivy:0.53.0 \
                image --format json --output /work/trivy-report.json \
                --severity HIGH,CRITICAL --exit-code 0 '"$IMAGE_NAME"'

              docker run -d --name miluim-grant -p 80:5000 --restart=always \
                -v ~/nice-devsecops/app/miluimData:/app/data '"$IMAGE_NAME"'
            EOSH
          '''
        }
      }
    }

    stage('Retrieve Report to Jenkins') {
      steps {
        sshagent (credentials: [env.SSH_CRED_ID]) {
          sh '''
            set -e
            # מושך את הדוח מהשרת לתיקיית ה-Workspace של Jenkins
            scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST}:~/nice-devsecops/app/trivy-report.json ./trivy-report.json
            ls -l ./trivy-report.json
          '''
        }
      }
    }

    stage('Upload Report to S3 (from Jenkins)') {
      steps {
        withCredentials([aws(credentialsId: env.AWS_CRED_ID,
                             accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                             secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {
          sh """
            set -e

            if [ ! -f ./trivy-report.json ]; then
              echo "trivy-report.json not found in workspace. Failing upload stage."
              exit 1
            fi

            if ! command -v aws >/dev/null 2>&1; then
              echo "Installing AWS CLI v2 locally on the agent..."
              curl -sS https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip
              unzip -q awscliv2.zip
              ./aws/install || true
            fi

            aws --version || true

            aws s3 cp ./trivy-report.json s3://$BUCKET/reports/trivy-$(date +%s).json --region $AWS_REGION
          """
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'trivy-report.json', onlyIfSuccessful: false
    }
  }
}