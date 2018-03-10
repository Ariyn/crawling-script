pipeline {
  agent none
  stages {
    stage('Test') {
      agent {
        docker {
          image '9df960'
        }
      }
      steps {
        sh 'python3 src/test.py'
        echo "Hello, Jenkins!"
      }
    }
    stage("Lint") {
        agent {
          docker {
            image 'pylint:latest'
          }
        }
        steps {
            sh 'pylint3 --rcfile=./pylint.cfg src/test.py>pylint.log'
            sh 'cat pylint.log'
        }
        post {
          always {
            step([
              $class                     : 'WarningsPublisher',
              parserConfigurations       : [[
                                                    parserName: 'PYLint',
                                                    pattern   : 'pylint.log'
                                            ]],
              unstableTotalAll           : '0',
              usePreviousBuildAsReference: true
            ])
          }
        }
    }
  }
}