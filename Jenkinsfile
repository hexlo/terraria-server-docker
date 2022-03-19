pipeline {
  environment {
    userName = "hexlo"
    imageName = "terraria-server-docker"
    // Set buildVersion to manually change the server version. Leave empty for defaulting to 'latest'
    buildVersion = 'latest'
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
            serverVersion = sh(script: "${WORKSPACE}/get-latest-version.sh", , returnStdout: true).trim()
          }
          else {
            serverVersion = buildVersion
          }
          
          versionTag = sh(script: "echo $serverVersion | sed 's/./&./g;s/\\.\$//'", , returnStdout:true).trim()
          echo "serverVersion=${serverVersion}"
          echo "versionTag=${versionTag}"
          echo "buildVersion=${buildVersion}"
          
        }
      }
    }
    stage('Building image') {
      steps{
        script {
          date = sh "echo \$(date +%Y-%m-%d:%H:%M:%S)"
          echo "date=$date"
          // Docker Hub
          dockerhubImage = docker.build( "${dockerhubRegistry}:${tag}", "--no-cache --build-arg VERSION=${buildVersion} --build-arg CACHE_DATE=$date ." )
          
          // Github
          githubImage = docker.build( "${githubRegistry}:${tag}", "--no-cache --build-arg VERSION=${buildVersion} --build-arg CACHE_DATE=$date ." )
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
            // dockerhubImage.push("${BUILD_NUMBER}")
          }
          // Github
          docker.withRegistry("https://${githubRegistry}", "${githubCredentials}" ) {
            githubImage.push("${tag}")
            githubImage.push("${versionTag}")
            // githubImage.push("${BUILD_NUMBER}")
          }
        }
      }
    }
    stage('Remove Unused docker image') {
      steps{
        // Docker Hub
        sh "docker rmi ${dockerhubRegistry}:${tag}"
        sh "docker rmi ${dockerhubRegistry}:${versionTag}"
        // sh "docker rmi ${dockerhubRegistry}:${BUILD_NUMBER}"
        
        // Github
        sh "docker rmi ${githubRegistry}:${tag}"
        sh "docker rmi ${githubRegistry}:${versionTag}"
        // sh "docker rmi ${githubRegistry}:${BUILD_NUMBER}"
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
