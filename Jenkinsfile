pipeline {
  agent any

  triggers {
    githubPush()
  }

  environment {
    REPO_URL   = 'https://github.com/arielhalevy123/nice-devsecops.git'
    REMOTE_HOST = '34.207.115.202'
    REMOTE_USER = 'ubuntu'
    IMAGE_NAME  = 'miluim-grant:latest'
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
        sshagent (credentials: ['ubuntu']) {
          sh """
            set -e
            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "
              set -e &&
              if [ -d ~/nice-devsecops ]; then
                cd ~/nice-devsecops && git pull origin main
              else
                git clone ${REPO_URL} ~/nice-devsecops
              fi &&
              cd ~/nice-devsecops/app &&
              docker stop miluim-grant || true &&
              docker rm   miluim-grant || true &&
              docker build -t ${IMAGE_NAME} . &&
              docker run -d --name miluim-grant -p 80:5000 --restart=always \\
                -v ~/nice-devsecops/app/miluimData:/app/data ${IMAGE_NAME}
            "
          """
        }
      }
    }
  }
}