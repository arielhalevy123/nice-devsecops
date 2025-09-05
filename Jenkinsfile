pipeline {
  agent any

  triggers { githubPush() }

  environment {
    REPO_URL    = 'https://github.com/arielhalevy123/nice-devsecops.git'
    REMOTE_HOST = '34.207.115.202'
    REMOTE_USER = 'ubuntu'
    SSH_CRED_ID = 'ssh-ec2-app'
    IMAGE_NAME  = 'miluim-grant:latest'

    AWS_CRED_ID = 'aws-jenkins-devsecops'
    BUCKET      = 'devsecops-scan-reports-ariel'
    AWS_REGION  = 'us-east-1'
  }

  stages {
    stage('Checkout') {
      steps {
        git url: REPO_URL, branch: 'main'
        sh '''
          set -e
          echo "Repo checked out. Current files:"
          ls -la
        '''
      }
    }

    stage('Build & Run on App Server') {
      steps {
        sshagent (credentials: [env.SSH_CRED_ID]) {
          sh '''
            set -e
            ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST "
              set -e &&
              if [ -d ~/nice-devsecops ]; then
                cd ~/nice-devsecops && git pull origin main
              else
                git clone $REPO_URL ~/nice-devsecops
              fi &&
              cd ~/nice-devsecops/app &&
              docker stop miluim-grant || true &&
              docker rm   miluim-grant || true &&
              docker build -t $IMAGE_NAME . &&
              docker run -d --name miluim-grant -p 80:5000 --restart=always \\
                -v ~/nice-devsecops/app/Data:/app/data $IMAGE_NAME
            "
          '''
        }
      }
    }

    stage('Trivy Scan (App Server)') {
      steps {
        sshagent (credentials: [env.SSH_CRED_ID]) {
          sh '''
            set -e
            ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST "
              set -e &&
              cd ~/nice-devsecops/app &&
              docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                -v \$(pwd):/work aquasec/trivy:0.53.0 \\
                image --format json --output /work/trivy-report.json \\
                --severity HIGH,CRITICAL --exit-code 0 $IMAGE_NAME &&
              ls -l trivy-report.json
            "
          '''
        }
      }
    }

    stage('Upload Trivy Report to S3') {
        steps {
            sshagent (credentials: [env.SSH_CRED_ID]) {
            withCredentials([aws(credentialsId: env.AWS_CRED_ID,
                                accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                                secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                sh '''
                set -e
                ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST "
                    set -e &&
                    cd ~/nice-devsecops/app &&
                    docker run --rm -v \$(pwd):/work \\
                    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \\
                    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \\
                    -e AWS_DEFAULT_REGION=$AWS_REGION \\
                    amazon/aws-cli \\
                    s3 cp /work/trivy-report.json s3://$BUCKET/reports/trivy-\$(date +%s).json --region $AWS_REGION
                "
                '''
            }
            }
        }
    }
  }
}