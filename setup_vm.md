# Setup VM on GCP

## SSH Keys creation

Check https://cloud.google.com/compute/docs/connect/create-ssh-keys . 
More specifically,
- Linux and macOS: https://cloud.google.com/compute/docs/connect/create-ssh-keys#linux-and-macos 
- Windows: https://cloud.google.com/compute/docs/connect/create-ssh-keys#windows-10-or-later

If you have gitbash, ssh-keygen command is supported. 
- Create .ssh folder under user folder 
  - Windows: C:\USERS\YOUR_USER_NAME
  - Linux: ~
- Run the command: 

  - Linux/gitbash  `ssh-keygen -t rsa -f ~/.ssh/YOUR_USER_NAME -C YOUR_USER_NAME -b 2048`
  - Windows `ssh-keygen -t rsa -f C:\USERS\YOUR_USER_NAME\.ssh\KEY_FILENAME -C YOUR_USER_NAME -b 2048`

This will generate public and private keys.
Go to Compute Engine: https://console.cloud.google.com/compute and add the public key (KEY_FILENAME.pub).
`GCP->Compute Engine->Metadata->ssh-keys->Add key`

## VM instance creation

`GCP->Compute Engine->VM instances->Create instance`
`e2-standard-4`
`Ubuntu 20.14LTS 30GB`

It is convenient to give it a name

## Config file creation for SSH connection through Visual Studio Code

Create the config file under ~\.ssh folder (Modify the path file according to your OS):
Name of file: "config"
Contents:
    Host de-zoomcamp (name of the host/vm)
    
        Hostname 35.240.98.123 (external ip)
        User YOUR_USER_NAME
        IdentityFile c:/Users/YOUR_USER_NAME/.ssh/gcp

## Remote access to VM instance for installing all the tools

Use git bash, Windows command or similar. Change the path accordingly

  ssh -i /.ssh/gcp username@externalipofmachine (you can find the external ip of the VM in Google Cloud Console)
  username is the name of the user used when creating the ssh key

  Note that Google Cloud SDK is installed:
  gcloud --version:

  Google Cloud SDK 368.0.0
  alpha 2022.01.07
  beta 2022.01.07
  bq 2.0.72
  core 2022.01.07
  gsutil 5.6 
  minikube 1.24.0
  skaffold 1.35.1

## Download and install Anaconda for Linux in the vm instance

    mkdir bin
    cd bin
    wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
    bash Anaconda3-2021.11-Linux-x86_64.sh
      After installation choose yes to initialize Anaconda (adds some stuff in .bashrc to be executed each time user is logged in)
    type `source .bashrc` to login again and activate base environment

## Install docker in vm instance

    sudo apt-get update (to fetch the list of packages)
    sudo apt-get install docker.io

### Setup docker to be run without sudo:
    sudo groupadd docker  
    sudo usermod -aG docker $USER  
    newgrp docker  
    Test with `docker run hello-world` 
    
  If this method does not work, use:  

    sudo groupadd docker
    sudo gpasswd -a $USER docker
    sudo service docker restart
    source .bashrc
    Test with `docker run hello-world`  

## Install docker compose in vm instance

https://github.com/docker/compose/releases  
https://github.com/docker/compose/releases/download/v2.2.3/docker-compose-linux-x86_64  
    mkdir bin  
    cd bin  
    wget https://github.com/docker/compose/releases/download/v2.2.3/docker-compose-linux-x86_64 -O docker-compose  
    chmod +x docker-compose  
Test with `./docker-compose version`  
Add docker-compose to the path variable:  
    cd ..  
    nano .bascrc  
    Add export PATH?"${HOME}/bin:${PATH}"  
    Ctro+O to save  
    Ctrl+x  
    source .bashrc  
    which docker-compose  
...to test or docker-compose version  

## Clone repo in vm instance
Go to the home directory  
`cd`  

In github, fork the following repository, this will copy the repository in your github account:  
    https://github.com/MarcosMJD/ghcn-d.git  

Then, in the vm, clone the forked project repository:  
    git clone https://github.com/YOUR_GIT_USERNAME/ghcn-d.git  

## Setup Visual Studio Code in local machine to use the VM machine

Install Remote-SSH extension in VSC  
Click on green button in left-bottom corner. Connect to host. de-zoomcamp is listed because config file is opened.  
Open remote folder to have access to all repository files.  
Setup VSC to port forward so that we can interact with remote services.  
CTRL+T to see terminal  
  Ports tab. Add Port. 8080 to localhost:8080  
You will have terminal opened already to continue performing commands instead of using external bash  

## Install Terraform

Download the binary to the /bin directory  
    wget https://releases.hashicorp.com/terraform/1.1.4/terraform_1.1.4_linux_amd64.zip  
    cd /bin  
    sudo apt-get install unzip  
    unzip terraform_1.1.4_linux_amd64.zip  
    terraform -version  

## GCP SDK 

GCP SDK is already installed in the VM.  
Upload the json file with the credentials generated through Google Cloud when creating the service account.  
If you use Visual Studio Code, just drag and drop the file
Set the GOOGLE_APPLICATION_CREDENTIALS to the credentials file: 

`export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.google/credentials/google_credentials.json"  `

Edit `.bashrc` to add it permanently:  

    export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.google/credentials/google_credentials.json"
    source ~/.bashrc
Perform de authentication:  

`gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS`  





