pipeline {
  environment {
    userName = "hexlo"
    imageName = "terraria-server-docker"
    // Set buildVersion to manually change the server version. Leave empty for defaulting to 'latest'
    buildVersion = '1442'
    tag = "${buildVersion ? buildVersion : 'latest'}"
    gitRepo = "https://github.com/${userName}/${imageName}.git"
    dockerhubRegistry = "${userName}/${imageName}"
    githubRegistry = "ghcr.io/${userName}/${imageName}"
    
    dockerhubCredentials = 'DOCKERHUB_TOKEN'
    githubCredentials = 'GITHUB_TOKEN'
    
    dockerhubImage = ''
    dockerhubImageLatest = ''
    githubImage = ''
    
    serverVersion = ''
    versionTag = ''
  }
  agent any
  triggers {
        cron('H H(4-6) * * *')
  }
  stages {
    stage('Cloning Git') {
      steps {
        git branch: 'main', credentialsId: 'GITHUB_TOKEN', url: gitRepo
      }
    }
    stage('Getting Latest Version') {
      steps {
        script {
          echo "tag=${tag}"
          if (tag == 'latest') {
            latestVersion = sh(script: "${WORKSPACE}/.scripts/get-terraria-version.sh", returnStdout: true).trim()
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
    stage('Building image') {
      steps{
        script {
          // Docker Hub
          dockerhubImage = docker.build( "${dockerhubRegistry}:${tag}", "--no-cache --build-arg VERSION=${buildVersion} ." )
          
          // Github
          githubImage = docker.build( "${githubRegistry}:${tag}", "--no-cache --build-arg VERSION=${buildVersion} ." )
        }
      }
    }
    stage('Deploy Image') {
      steps{
        script {
          // Docker Hub
          docker.withRegistry( '', "${dockerhubCredentials}" ) {
            dockerhubImage.push("${tag}")
            dockerhubImage.push("${versionTag}")
          }
          // Github
          docker.withRegistry("https://${githubRegistry}", "${githubCredentials}" ) {
            githubImage.push("${tag}")
            githubImage.push("${versionTag}")
          }
        }
      }
    }
    stage('Remove Unused docker image') {
      steps{
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
          // Docker Hub
          sh "docker rmi ${dockerhubRegistry}:${tag}"
          sh "docker rmi ${dockerhubRegistry}:${versionTag}"

          // Github
          sh "docker rmi ${githubRegistry}:${tag}"
          sh "docker rmi ${githubRegistry}:${versionTag}"
        }

      }
    }
  }
  post {
    failure {
        mail bcc: '', body: "<b>Jenkins Build Report</b><br>Project: ${env.JOB_NAME} <br>Build Number: ${env.BUILD_NUMBER} \
        <br>Build URL: ${env.BUILD_URL}", cc: '', charset: 'UTF-8', from: '', mimeType: 'text/html', replyTo: '', \
        subject: "Jenkins Build Failed: ${env.JOB_NAME}", to: "jenkins@mindlab.dev";  

    }
  }
}
