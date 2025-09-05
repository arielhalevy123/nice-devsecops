pipeline {
  agent any

  environment {
    REPO_URL    = 'https://github.com/arielhalevy123/nice-devsecops.git'

    // שרת האפליקציה (EC2)
    REMOTE_HOST = '34.207.115.202'
    REMOTE_USER = 'ubuntu'

    // שמות הקרדנצ׳יאלס כפי שמוגדרים ב-Jenkins
    SSH_CRED_ID = 'ssh-ec2-app'
    AWS_CRED_ID = 'aws-jenkins-devsecops'  // access key + secret key

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

          // מריצים רק אם קיים infra/ ועל הסוכן יש tofu מותקן
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
    sshagent (credentials: [SSH_CRED_ID]) {
      sh """
        set -e
        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} '
          set -e

          # 1) ודא ש-Docker מותקן
          if ! command -v docker >/dev/null 2>&1; then
            echo "Docker not found - installing..."
            sudo curl -fsSL https://get.docker.com | sudo sh
            sudo systemctl enable --now docker || true
          fi

          # 2) עדכון קוד האפליקציה
          if [ -d ~/nice-devsecops ]; then
            cd ~/nice-devsecops && git pull origin main
          else
            git clone ${REPO_URL} ~/nice-devsecops
          fi

          cd ~/nice-devsecops/app

          # 3) עצירת קונטיינר ישן (אם קיים)
          sudo docker stop miluim-grant || true
          sudo docker rm   miluim-grant || true

          # 4) בניית אימג'
          sudo docker build -t ${IMAGE_NAME} .

          # 5) סריקת Trivy (בלי להכשיל את ה-Pipeline)
          sudo docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
            aquasec/trivy:0.53.0 image --severity HIGH,CRITICAL --exit-code 0 ${IMAGE_NAME} || true

          # 6) הרצת הקונטיינר על פורט 80 ← 5000 של האפליקציה
          sudo docker run -d --name miluim-grant -p 80:5000 --restart=always \\
            -v ~/nice-devsecops/app/miluimData:/app/data ${IMAGE_NAME}
        '
      """
    }
  }
}
    stage('Upload Report to S3 (from Jenkins)') {
      steps {
        withCredentials([aws(credentialsId: env.AWS_CRED_ID,
          accessKeyVariable: 'AWS_ACCESS_KEY_ID',
          secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {

          sh '''
            set -e
            if ! command -v aws >/dev/null 2>&1; then
              echo "Installing AWS CLI v2 locally on the agent..."
              curl -sS https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip
              unzip -q awscliv2.zip
              sudo ./aws/install || ./aws/install
            fi

            # מעלים את הדוח ל-S3 (מצד Jenkins)
            aws s3 cp ./trivy-report.json s3://$BUCKET/reports/trivy-$(date +%s).json --region $AWS_REGION
          '''
        }
      }
    }
  }
}