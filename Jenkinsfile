pipeline {
  agent any

  environment {
    REPO_URL    = 'https://github.com/arielhalevy123/nice-devsecops.git'
    REMOTE_HOST = '34.207.115.202'  
    REMOTE_USER = 'ubuntu'
    SSH_CRED_ID = 'ssh-ec2-app'
    IMAGE_NAME  = 'miluim-grant:latest'
    BUCKET      = 'devsecops-scan-reports-ariel'
    AWS_REGION  = 'us-east-1'
  }

  stages {
    stage('Checkout') {
      steps { git url: REPO_URL, branch: 'main' }
    }

    stage('Provision Infra (OpenTofu)') {
      steps {
        withCredentials([aws(credentialsId: 'aws-jenkins-devsecops',
          accessKeyVariable: 'AWS_ACCESS_KEY_ID',
          secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {

          sh """
            set -e
            cd infra
            tofu init -upgrade
            tofu plan -var-file=dev.tfvars -out=tfplan
            tofu apply -auto-approve tfplan
          """
        }
      }
    }

    stage('Build + Scan + Deploy (over SSH)') {
      steps {
        sshagent (credentials: [SSH_CRED_ID]) {
          withCredentials([aws(credentialsId: 'aws-jenkins-devsecops',
            accessKeyVariable: 'AWS_ACCESS_KEY_ID',
            secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {

            sh """
              set -e

              ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} '
                set -e

                if [ -d ~/nice-devsecops ]; then
                  cd ~/nice-devsecops && git pull origin main
                else
                  git clone ${REPO_URL} ~/nice-devsecops
                fi

                cd ~/nice-devsecops/app

                docker stop miluim-grant || true
                docker rm   miluim-grant || true

                docker build -t ${IMAGE_NAME} .

                docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                  -v \$(pwd):/work aquasec/trivy:0.53.0 \
                  image --format json --output /work/trivy-report.json \
                  --severity HIGH,CRITICAL --exit-code 0 ${IMAGE_NAME}

                if ! command -v aws >/dev/null 2>&1; then
                  curl -sS "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                  unzip -q awscliv2.zip
                  sudo ./aws/install
                fi

                AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
                aws s3 cp trivy-report.json s3://${BUCKET}/reports/trivy-$(date +%s).json --region ${AWS_REGION}

                docker run -d --name miluim-grant -p 80:5000 --restart=always \\
                  -v ~/nice-devsecops/app/miluimData:/app/data ${IMAGE_NAME}
              '
            """
          }
        }
      }
    }
  }
}