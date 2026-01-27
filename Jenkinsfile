pipeline {
  environment {
    userName = "hexlo"
    imageName = "terraria-server-docker"
    // Set buildVersion to manually change the server version. Leaving empty will default to 'latest'
    buildVersion = 'latest'
    tag = "${buildVersion ? buildVersion : 'latest'}"
    gitRepo = "https://github.com/${userName}/${imageName}.git"
    gitBranch = "main"
    dockerhubRegistry = "${userName}/${imageName}"
    githubRegistry = "ghcr.io/${userName}/${imageName}"
    arch=''
    
    dockerhubCredentials = 'DOCKERHUB_TOKEN'
    githubCredentials = '3801c6bb-4368-4484-8c3a-42c0a779fe10'
    jenkins_email = credentials('RUNX_EMAIL')
    
    dockerhubImage = ''
    dockerhubImageLatest = ''
    githubImage = ''
    
    serverVersion = ''
    versionTag = ''
  }
  agent any
  triggers {
        cron('H * * * *')
  }
  stages {
    stage('Cloning Git') {
      steps {
        git branch: "${gitBranch}", credentialsId: 'GITHUB_TOKEN', url: "${gitRepo}"
      }
    }
    stage('Getting Latest Version') {
      steps {
        script {
          echo "tag=${tag}"
          if (tag == 'latest') {
            latestVersion = sh(script: "${WORKSPACE}/.scripts/get-terraria-version.sh", returnStdout: true).trim()
            echo "latestVersion: ${latestVersion}"
            versionTag = sh(script: "echo $latestVersion | sed 's/[0-9]/&./g;s/\\.\$//'", returnStdout:true).trim()
          }
          else {
            versionTag = sh(script: "echo $buildVersion | sed 's/[0-9]/&./g;s/\\.\$//'", returnStdout:true).trim()
          }
          echo "versionTag=${versionTag}"
          echo "buildVersion=${buildVersion}"
        }
      }
    }
    stage('Creating buildx builder') {
      steps {
        script {
          catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
            sh "docker buildx create --name multiarch --use"
          }
        }
      }
      
    }
    stage('Building amd64 image') {
      steps{
        script {
          arch='amd64'
          echo "Building ${dockerhubRegistry}-${arch}"
          // Docker Hub
          sh "docker buildx use multiarch"
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:${tag} --load ."
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:${versionTag} --load ."

          // Github
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${githubRegistry}-${arch}:${tag} --load ."
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${githubRegistry}-${arch}:${versionTag} --load ."
        }
      }
    }
    stage('Building arm64 image') {
      steps{
        script {
          arch='arm64'
          echo "Building ${dockerhubRegistry}-${arch}"

          // Global
          sh "docker buildx use multiarch"

          // Docker Hub
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:${tag} --load ."
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:${versionTag} --load ."

          // Github
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${githubRegistry}-${arch}:${tag} --load ."
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${githubRegistry}-${arch}:${versionTag} --load ."
        }
      }
    }
    stage('Deploy Image - Dockerhub') {
      steps{
        script {
          docker.withRegistry( '', "${dockerhubCredentials}" ) {
            // Push individual images for them to be available to the manifest
            sh "docker push ${dockerhubRegistry}-amd64:${tag}"
            sh "docker push ${dockerhubRegistry}-arm64:${tag}"

            sh "docker push ${dockerhubRegistry}-amd64:${versionTag}"
            sh "docker push ${dockerhubRegistry}-arm64:${versionTag}"

            // Better way using imagetools. Need testing
            // docker buildx imagetools create --progress plain hexlo/terraria-server-docker-amd64:latest hexlo/terraria-server-docker-arm64 --tag hexlo/terraria-server-docker:latest

            echo "creating manifest"

            sh "docker manifest create --amend ${dockerhubRegistry}:${tag} ${dockerhubRegistry}-amd64:${tag} ${dockerhubRegistry}-arm64:${tag}"
            sh "docker manifest push ${dockerhubRegistry}:${tag}"

            sh "docker manifest create --amend ${dockerhubRegistry}:${versionTag} ${dockerhubRegistry}-amd64:${versionTag} ${dockerhubRegistry}-arm64:${versionTag}"
            sh "docker manifest push ${dockerhubRegistry}:${versionTag}"
          }
        }
      }
    }

    stage('Deploy Image - ghcr.io') {
      steps{
        script {

          withCredentials([string(credentialsId: ${githubCredentials}, variable: 'GITHUB_TOKEN')]) {

            echo "====================== Deploy Image - ghcr.io ========================================\n\n\n\n\n"
            // Push individual images for them to be available to the manifest
            sh "docker push ${githubRegistry}-amd64:${tag}"
            sh "docker push ${githubRegistry}-arm64:${tag}"

            sh "docker push ${githubRegistry}-amd64:${versionTag}"
            sh "docker push ${githubRegistry}-arm64:${versionTag}"

            // Better way using imagetools. Need testing
            // docker buildx imagetools create --progress plain hexlo/terraria-server-docker-amd64:latest hexlo/terraria-server-docker-arm64 --tag hexlo/terraria-server-docker:latest

            echo "creating manifest"

            sh "docker manifest create --amend ${githubRegistry}:${tag} ${githubRegistry}-amd64:${tag} ${githubRegistry}-arm64:${tag}"
            sh "docker manifest push ${githubRegistry}:${tag}"

            sh "docker manifest create --amend ${githubRegistry}:${versionTag} ${githubRegistry}-amd64:${versionTag} ${githubRegistry}-arm64:${versionTag}"
            sh "docker manifest push ${githubRegistry}:${versionTag}"
          }
        }
      }
    }

  }
  post {
    always {
        // Cleanup of docker images and volumes
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
          // Docker Hub
          sh "docker rmi -f ${dockerhubRegistry}:${tag}"
          sh "docker rmi -f ${dockerhubRegistry}:${versionTag}"

          sh "docker rmi -f ${dockerhubRegistry}-amd64:${tag}"
          sh "docker rmi -f ${dockerhubRegistry}-amd64:${versionTag}"

          sh "docker rmi -f ${dockerhubRegistry}-arm64:${tag}"
          sh "docker rmi -f ${dockerhubRegistry}-arm64:${versionTag}"

          // Github
          sh "docker rmi -f ${githubRegistry}:${tag}"
          sh "docker rmi -f ${githubRegistry}:${versionTag}"

          sh "docker rmi -f ${githubRegistry}-amd64:${tag}"
          sh "docker rmi -f ${githubRegistry}-amd64:${versionTag}"
          
          sh "docker rmi -f ${githubRegistry}-arm64:${tag}"
          sh "docker rmi -f ${githubRegistry}-arm64:${versionTag}"

          // Global
          sh "docker system prune --all --force --volumes"
        }
    }
    failure {
        mail bcc: '', body: "<b>Jenkins Build Report</b><br>Project: ${env.JOB_NAME} <br>Build Number: ${env.BUILD_NUMBER} \
        <br>Build URL: ${env.BUILD_URL}", cc: '', charset: 'UTF-8', from: '', mimeType: 'text/html', replyTo: '', \
        subject: "Jenkins Build Failed: ${env.JOB_NAME}", to: "${jenkins_email}";  

    }
  }
}
