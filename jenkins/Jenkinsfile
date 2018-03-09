pipeline {
  agent none
  stages {
    stage('Test') {
      agent {
        docker {
          image 'frolvald/alpine-python3'
        }
      }
      steps {
        sh 'python3 src/test.py'
      }
      post {
          always {
              junit 'test-reports/results.xml'
          }
      }
    }
  }
}