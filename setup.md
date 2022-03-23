# Setup VM on GCP

## SSH Keys creation

Check https://cloud.google.com/compute/docs/connect/create-ssh-keys and https://cloud.google.com/compute/docs/connect/create-ssh-keys#linux-and-macos or https://cloud.google.com/compute/docs/connect/create-ssh-keys#windows-10-or-later

Use gitbash to run the command  

    `ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USER -b 2048`
Need to create .ssh folder under user folder  

    `GCP->Compute Engine->Metadata->ssh-keys->Add key`
Add the public key

## VM instance creation

Enable 
`GCP->Compute Engine->VM instances->Create instance`
` Ubuntu 20.14LTS 30GB`

Store the keys under User/.../.ssh
i.e. gcp file is the private key

## Config file creation for SSH connection

Create the config file:
Host de-zoomcamp (name of the host/vm)

    Hostname 35.240.98.123 (external ip)
    User marcos
    IdentityFile c:/Users/Marcos/.ssh/gcp

## Remote access to VM instance

Git bash
  ssh -i /.ssh/gcp marcos@externalipofmachine
  marcos is the name of the user used when creating the ssh key

  Google Cloud SDK is installed:
  gcloud --version:

  Google Cloud SDK 368.0.0
  alpha 2022.01.07
  beta 2022.01.07
  bq 2.0.72
  core 2022.01.07
  gsutil 5.6 
  minikube 1.24.0
  skaffold 1.35.1

## Download Anaconda for Linux in the vm instance

  wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
  bash Anaconda-3...
  After installation choose yes to initialize Anaconda (adds in .bashrc some stuff to be executed each time user is logged in)
  CTRL+D to logout
  After log in, base env is already activated.

## Install docker in vm instance

sudo apt-get update (to fetch the list of packages)
sudo apt-get install docker.io
Setup docker to be run without sudo
  sudo groupadd docker
  sudo gpasswd -a $USER docker
  sudo service docker restart
  Relog user
  Test with docker run hello-world

## Install docker compose in vm instance

https://github.com/docker/compose/releases
https://github.com/docker/compose/releases/download/v2.2.3/docker-compose-linux-x86_64
mkdir bin
cd bin
wget https://github.com/docker/compose/releases/download/v2.2.3/docker-compose-linux-x86_64 -O docker-compose
chmod +x docker-compose
Test with ./docker-compose version
Add docker-compose to the path variable
cd .. 
nano .bascrc
Add export PATH?"${HOME}/bin:${PATH}"
Ctro+O to save
Ctrl+x
source .bashrc to relogin
which docker-compose to test or docker-compose version

## Clone repo in vm instance
Clone the project repository:
git clone https://github.com/MarcosMJD/ghcn-d.git


By running docker-compose up -d will run the yaml file to run postgresql and pgadmin in detached mode

## Install pgcli

Pip install pgcli
pgcli -h localhost -U root
\dt to check
Note: Some error will be shown but it works
To fix:
pip uninstall pgcli
conda install -c conda-forge pgcli
pip install -U mycli

## Setup VSC in local machine to use the VM machine

Install Remote-SSH extension in VSC
Click on green button in left-bottom corner. Connect to host. de-zoomcamp is listed because config file is opened.

Setup VSC to port forward so that we can interact with remote postgres and pgadmin from local machine
CTRL+T to see terminal
Ports tab. Add Port. 5432 to localhost:5432
The same with 80 to 8085
Then open a terminal and run pgcli.exe -h localhost -U root -d ny_taxi
(stop any local instance of postgresql before)
Note error is shown but works

## Run jupyternote in remote machine to execute the ingestion notebook to load data into database

Note: Close any local instance of jupyter
In remote terminal (the one in VSC) execute: jupiter notebook
Auto port forwarding is done
In a browser, open http://localhost:8888/?token=e453799176773588a2be6ff2e49fdf9c82356f306d791e76
Download the datafile with wget 
Run the jupyter script
Note !wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv :  ! to execute commands

## Install Terraform

We will not use the package manager, but download the binary to the /bin directory
wget https://releases.hashicorp.com/terraform/1.1.4/terraform_1.1.4_linux_amd64.zip
cd /bin
sudo apt-get install unzip
unzip terraform_1.1.4_linux_amd64.zip
terraform -version










## GCP SDK 

GCP SDK is already installed in the VM.  
Upload the json file with the credentials generated through Google Cloud when creating the service account.  
Set the GOOGLE_APPLICATION_CREDENTIALS to the credentials file: 

`export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.google/credentials/google_credentials.json"  `

Edit `.bashrc` to add it permanently:  

    export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.google/credentials/google_credentials.json"
    source ~/.bashrc
Perform de authentication:  

`gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS`  

## Install Spark?




