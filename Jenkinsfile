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
            sh 'ls'
            sh 'cat pylint.cfg'
            sh 'pylint3 --rcfile=./pylint.cfg src/*>pylint.log'
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