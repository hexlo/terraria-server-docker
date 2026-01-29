pipeline {
  environment {
    def userName = "hexlo"
    def imageName = "terraria-server-docker"
    // Set buildVersion to manually change the server version. Leaving empty will default to 'latest'. Use '1234' format.
    def buildVersion = ''
    def tag = "${buildVersion ? buildVersion : 'latest'}"
    def gitRepo = "https://github.com/${userName}/${imageName}.git"
    def gitBranch = "main"
    def dockerhubRegistry = "${userName}/${imageName}"
    def githubRegistry = "ghcr.io/${userName}/${imageName}"
    def arch=''
    
    def dockerhubCredentials = 'DOCKERHUB_TOKEN'
    def githubCredentials = 'GITHUB_TOKEN'
    def jenkins_email = credentials('RUNX_EMAIL')
    
    def dockerhubImage = ''
    def dockerhubImageLatest = ''
    def githubImage = ''
    
    def serverVersion = ''
    def versionTag = ''
  }
  agent any
  triggers {
        cron('H * * * *')
  }
  stages {
    stage('Cloning Git') {
      steps {
        git branch: "${gitBranch}", credentialsId: "${githubCredentials}", url: "${gitRepo}"
      }
    }

    stage('Installing dependencies') {
      steps {
        script {
          echo "========== ${env.STAGE_NAME} =========="
          sh "python3 --version"

          // installing regclient
          sh "curl -L https://github.com/regclient/regclient/releases/latest/download/regctl-linux-amd64 >regctl"
          sh "chmod 755 regctl"

          sh "./regctl version"

          // # login to GHCR with a provided password
          withCredentials([string(credentialsId: 'f1ed1fe0-50bf-4256-9d08-029f48737802', variable: 'TOKEN')]) {
              sh """echo ${TOKEN} | ./regctl registry login ghcr.io -u ${userName} --pass-stdin"""     
          }

        }
      }
    }

    stage('get_latest_version Tests') {
      steps {
        script {
          echo "========== Running Unit Tests =========="
          sh "python3 tests/test_get_next_version.py -v"
        }
      }
    }

    stage('Getting Latest Version') {
      steps {
        script {
          echo "========== Getting Terraria's Latest Available Version =========="
          echo "tag=${tag}"
          if (tag == 'latest') {
            def latestVersion = sh(script: "python3 ${WORKSPACE}/scripts/get_latest_version.py | tail -n 1", returnStdout: true).trim()
            if (latestVersion.isEmpty()) {
              echo "Warning: Failed to get latest version, using default 'latest' tag"
              env.versionTag = 'latest'
            } else {
              echo "latestVersion: ${latestVersion}"
              env.versionTag = sh(script: "echo ${latestVersion} | sed 's/[0-9]/&./g;s/\\.\$//'", returnStdout: true).trim()
              echo "versionTag: ${env.versionTag}"
            }
          }
          else {
            env.versionTag = sh(script: "echo ${env.buildVersion} | sed 's/[0-9]/&./g;s/\\.\$//'", returnStdout: true).trim()
            echo "buildVersion=${env.buildVersion}, versionTag=${env.versionTag}"
          }
        }
      }
    }

    stage('Creating buildx builder') {
      steps {
        script {
          echo "========== Creating buildx builder =========="

          catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
            sh "docker buildx create --name multiarch --use"
          }
        }
      }
      
    }

    stage('Building Images - Docker Hub') {
      steps {
        script {
          arch='amd64'
          echo "========== Building ${dockerhubRegistry}-${arch} =========="

          sh "docker buildx use multiarch"
          sh "docker buildx build --build-arg VERSION=${env.buildVersion} --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:latest --load ."
          sh "docker buildx build --build-arg VERSION=${env.buildVersion} --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:${versionTag} --load ."

          arch='arm64'
          echo "========== Building ${dockerhubRegistry}-${arch} =========="

          sh "docker buildx build --build-arg VERSION=${env.buildVersion} --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:latest --load ."
          sh "docker buildx build --build-arg VERSION=${env.buildVersion} --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:${versionTag} --load ."
        }
      }
    }

    stage('Deploy Images to Dockerhub') {
      steps{
        script {
          echo "========== Deploy Images to Dockerhub =========="
          docker.withRegistry( '', "${dockerhubCredentials}" ) {
            // Push individual images for them to be available to the manifest
            sh "docker push ${dockerhubRegistry}-amd64:latest"
            sh "docker push ${dockerhubRegistry}-arm64:latest"

            sh "docker push ${dockerhubRegistry}-amd64:${env.versionTag}"
            sh "docker push ${dockerhubRegistry}-arm64:${env.versionTag}"

            // Better way using imagetools. Need testing
            // docker buildx imagetools create --progress plain hexlo/terraria-server-docker-amd64:latest hexlo/terraria-server-docker-arm64 --tag hexlo/terraria-server-docker:latest

            echo "creating manifest"

            sh "docker manifest create --amend ${dockerhubRegistry}:latest ${dockerhubRegistry}-amd64:latest ${dockerhubRegistry}-arm64:latest"
            sh "docker manifest push ${dockerhubRegistry}:latest"

            sh "docker manifest create --amend ${dockerhubRegistry}:${env.versionTag} ${dockerhubRegistry}-amd64:${env.versionTag} ${dockerhubRegistry}-arm64:${env.versionTag}"
            sh "docker manifest push ${dockerhubRegistry}:${env.versionTag}"
          }
        }
      }
    }

    stage('Copying Images to ghcr.io') {
      steps {
        script {
          echo "========== ${env.STAGE_NAME} =========="
          sh "./regctl image copy ${dockerhubRegistry}:latest ${githubRegistry}:latest"
          sh "./regctl image copy ${dockerhubRegistry}:${env.versionTag} ${githubRegistry}:${env.versionTag}"
        }
      }
    }
  }
  post {
    always {
        // Cleanup of docker images and volumes
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
          // Docker Hub
          sh "docker rmi -f ${dockerhubRegistry}:latest"
          sh "docker rmi -f ${dockerhubRegistry}:${env.versionTag}"

          sh "docker rmi -f ${dockerhubRegistry}-amd64:latest"
          sh "docker rmi -f ${dockerhubRegistry}-amd64:${env.versionTag}"

          sh "docker rmi -f ${dockerhubRegistry}-arm64:latest"
          sh "docker rmi -f ${dockerhubRegistry}-arm64:${env.versionTag}"

          // Global
          sh "docker system prune --all --force --volumes"
        }
    }
  //   failure {
  //       mail bcc: '', body: "<b>Jenkins Build Report</b><br>Project: ${env.JOB_NAME} <br>Build Number: ${env.BUILD_NUMBER} \
  //       <br>Build URL: ${env.BUILD_URL}", cc: '', charset: 'UTF-8', from: '', mimeType: 'text/html', replyTo: '', \
  //       subject: "Jenkins Build Failed: ${env.JOB_NAME}", to: "${jenkins_email}";  

  //   }
  }
}
