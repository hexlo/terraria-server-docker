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
    githubCredentials = 'GITHUB_TOKEN'
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
      environment { HOME = "${env.WORKSPACE}" }
      steps {
        git branch: "${gitBranch}", credentialsId: 'GITHUB_TOKEN', url: "${gitRepo}"
      }
    }
    stage('Getting Latest Version') {
      environment { HOME = "${env.WORKSPACE}" }
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
      environment { HOME = "${env.WORKSPACE}" }
      steps {
        script {
          catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
            sh "docker buildx create --name multiarch --use"
          }
        }
      }
      
    }
    stage('Building amd64 image') {
      environment { HOME = "${env.WORKSPACE}" }
      steps{
        script {
          arch='amd64'
          "Building ${dockerhubRegistry}-${arch}"
          // Docker Hub
          // dockerhubImage = docker.build( "${dockerhubRegistry}-${arch}:${tag}", "--target build-amd64 --platform linux/amd64 --no-cache --build-arg VERSION=${buildVersion} ." )
          // dockerhubImage = docker.build( "${dockerhubRegistry}-${arch}:${versionTag}", "--target build-amd64 --platform linux/amd64 --no-cache --build-arg VERSION=${buildVersion} ." )
          sh "docker buildx use multiarch"
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:${tag} --load ."
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:${versionTag} --load ."

          // Github
          // githubImage = docker.build( "${githubRegistry}-${arch}:${tag}", "--target build-amd64 --platform linux/amd64 --no-cache --build-arg VERSION=${buildVersion} ." )
        }
      }
    }
    stage('Building arm64 image') {
      environment { HOME = "${env.WORKSPACE}" }
      steps{
        script {
          arch='arm64'
          echo "Building ${dockerhubRegistry}-${arch}"
          // Docker Hub
          sh "docker buildx use multiarch"
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:${tag} --load ."
          sh "docker buildx build --builder multiarch --target build-${arch} --no-cache --progress plain --platform linux/${arch} -t ${dockerhubRegistry}-${arch}:${versionTag} --load ."

          // Github
          // githubImage = docker.build( "${githubRegistry}-${arch}:${tag}", "--target build-arm64 --platform linux/arm64 --no-cache --build-arg VERSION=${buildVersion} ." )
        }
      }
    }
    stage('Deploy Image') {
      environment { HOME = "${env.WORKSPACE}" }
      steps{
        script {
          // Docker Hub
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
          // Github
          // docker.withRegistry("https://${githubRegistry}", "${githubCredentials}" ) {
          //   githubImage.push("${tag}")
          //   githubImage.push("${versionTag}")
          // }
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
          sh "docker rmi -f ${dockerhubRegistry}-arm64:${tag}"

          // Github
          sh "docker rmi -f ${githubRegistry}:${tag}"
          sh "docker rmi -f ${githubRegistry}:${versionTag}"

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
