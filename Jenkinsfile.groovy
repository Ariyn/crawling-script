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
            sh 'ls -al'
            sh 'pylint3 --rcfile=./pylint.cfg --reports no src/*>pylint.log||exit 0'
            sh 'cat pylint.log'
            step([
              $class                     : 'WarningsPublisher',
              parserConfigurations       : [[
                                              parserName: 'PYLint',
                                              pattern   : 'pylint.log'
                                            ]],
              healthy                    : '10',
              usePreviousBuildAsReference: false
            ])
        }
    }
  }
}