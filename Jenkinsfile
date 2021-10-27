pipeline {
  environment {
    gitRepo = "https://github.com/Iceoid/terraria-server-docker.git"
    imageName = "terraria-server-docker"
    dockerhubRegistry = "iceoid/terraria-server"
    githubRegistry = "ghcr.io/iceoid/$imageName"
    dockerhubCredentials = 'DOCKERHUB_TOKEN'
    githubCredentials = 'GITHUB_TOKEN'
    
    dockerhubImage = ''
    dockerhubImageLatest = ''
    githubImage = ''
  }
  agent any
  stages {
    stage('Cloning Git') {
      steps {
        git branch: 'main', credentialsId: 'GITHUB_TOKEN', url: gitRepo
      }
    }
    stage('Building image') {
      steps{
        script {
          dockerhubImageLatest = docker.build dockerhubRegistry + ":latest"
          
          githubImage = docker.build githubRegistry + ":latest"
        }
      }
    }
    stage('Deploy Image') {
      steps{
        script {
          docker.withRegistry( '', dockerhubCredentials ) {
            dockerhubImageLatest.push()
          }
          docker.withRegistry('https://' + githubRegistry, githubCredentials) {
            githubImage.push()
          }
        }
      }
    }
    stage('Remove Unused docker image') {
      steps{
        sh "docker rmi $dockerhubRegistry:latest"
        sh "docker rmi $githubRegistry:latest"
      }
    }
  }
}
