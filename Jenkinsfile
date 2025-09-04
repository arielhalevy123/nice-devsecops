pipeline {
  agent any

  environment {
    REPO_URL    = 'https://github.com/arielhalevy123/nice-devsecops.git'

    // פרטי השרת שמריץ את האפליקציה (EC2 A)
    REMOTE_HOST = '34.207.115.202'
    REMOTE_USER = 'ubuntu'

    // IDs של הקרדנצ׳יאלס כפי שהוגדרו בג׳נקינס
    SSH_CRED_ID = 'ubuntu'                 // אם אצלך נקרא אחרת—עדכן פה
    AWS_CRED_ID = 'aws-jenkins-devsecops'  // Access key + Secret key

    // דוקר + S3
    IMAGE_NAME  = 'miluim-grant:latest'
    BUCKET      = 'devsecops-scan-reports-ariel'
    AWS_REGION  = 'us-east-1'
  }

  triggers {
    // חשוב כדי שה־Webhook יפעיל את ה־Job אוטומטית
    githubPush()
  }

  stages {
    stage('Checkout') {
      steps {
        git url: REPO_URL, branch: 'main'
      }
    }

    stage('Provision Infra (OpenTofu)') {
      steps {
        withCredentials([aws(credentialsId: env.AWS_CRED_ID,
          accessKeyVariable: 'AWS_ACCESS_KEY_ID',
          secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {

          // אם אין tofu על השרת, תראה שגיאה. אפשר להוסיף התקנה כאן אם תרצה.
          sh '''
            set -e
            if [ -d infra ]; then
              cd infra
              tofu -v || echo "NOTE: OpenTofu is not installed on this Jenkins agent."
              if command -v tofu >/dev/null 2>&1; then
                tofu init -upgrade
                # אין לנו dev.tfvars ברפו – מריצים בלי var-file
                tofu plan -out=tfplan
                tofu apply -auto-approve tfplan
              fi
            else
              echo "No infra/ directory found – skipping infra provisioning."
            fi
          '''
        }
      }
    }

    stage('Build + Scan + Deploy (over SSH)') {
      steps {
        sshagent (credentials: [env.SSH_CRED_ID]) {
          withCredentials([aws(credentialsId: env.AWS_CRED_ID,
            accessKeyVariable: 'AWS_ACCESS_KEY_ID',
            secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {

            sh '''
              set -e

              ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} '
                set -e

                # עדכון קוד מה-GitHub (clone ראשון או pull אם כבר קיים)
                if [ -d ~/nice-devsecops ]; then
                  cd ~/nice-devsecops && git pull origin main
                else
                  git clone ${REPO_URL} ~/nice-devsecops
                fi

                cd ~/nice-devsecops/app

                # עצירה וניקוי קונטיינר ישן אם קיים
                docker stop miluim-grant || true
                docker rm   miluim-grant || true

                # בניית אימג׳
                docker build -t ${IMAGE_NAME} .

                # סריקת טריווי על האימג׳ + הפקת דוח JSON בתיקיית הפרויקט
                docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                  -v "$(pwd)":/work aquasec/trivy:0.53.0 \
                  image --format json --output /work/trivy-report.json \
                  --severity HIGH,CRITICAL --exit-code 0 ${IMAGE_NAME}

                # התקנת AWS CLI אם צריך
                if ! command -v aws >/dev/null 2>&1; then
                  curl -sS "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                  unzip -q awscliv2.zip
                  sudo ./aws/install
                fi

                # העלאת הדוח ל-S3 – שים לב: אין צורך לברוח $, כי אנחנו בתוך בלוק ''' של Groovy
                AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
                aws s3 cp trivy-report.json s3://${BUCKET}/reports/trivy-$(date +%s).json --region ${AWS_REGION}

                # הרצת האפליקציה (חשיפת פורט 80 על ה־Host אל 5000 בקונטיינר)
                docker run -d --name miluim-grant -p 80:5000 --restart=always \
                  -v ~/nice-devsecops/app/miluimData:/app/data ${IMAGE_NAME}
              '
            '''
          }
        }
      }
    }
  }
}