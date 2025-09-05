pipeline {
  agent any

  triggers {
    githubPush()
  }

  stages {
    stage('Checkout') {
      steps {
        // מושך את הקוד מה-Repo שלך (main)
        git url: 'https://github.com/arielhalevy123/nice-devsecops.git', branch: 'main'
        sh '''
          set -e
          echo "Repo checked out. Current files:"
          ls -la
        '''
      }
    }
  }
}