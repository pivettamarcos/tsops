#!/bin/bash

CMD=${1:-install}
PREFIX=${2:-/usr/local/bin/}

install () {
  echo "Attempting to install minikube and assorted tools to $PREFIX"

  # install python
  sudo apt-get update \
	  && sudo apt-get install -y python3-pip python3-dev \
	  && pip3 install --upgrade pip \
	  && pip3 install virtualenv pyyaml setuptools kubernetes

  # install needed packages
  sudo apt -y install zlib1g zlib1g-dev libssl-dev python3-tk libreadline-dev libbz2-dev libffi-dev libsqlite3-dev

  if ! command minikube >/dev/null 2>&1; then
    curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    chmod +x minikube
    mv minikube "$PREFIX"
  else
    echo "minikube is already installed"
  fi

  # install pyenv
  curl https://pyenv.run | bash
  echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
  echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
  # echo 'eval "$(pyenv init -)"' >> ~/.bashrc

  source ~/.bashrc
}

start (){
    echo "Enter number of cpu cores"
	read CPU
	echo "Enter memory in MB"
    read MEMORY
    echo "Starting minikube..."
    minikube start --cpus $CPU --memory $MEMORY --ports=30000:30000,30001:30001,30002:30002
    
    curl -s "https://raw.githubusercontent.com/kserve/kserve/release-0.12/hack/quick_install.sh" | bash

    echo "Setting MLFLOW_TRACKING_URI and MLFLOW_S3_ENDPOINT_URL env variables in .bashrc"
    echo 'export MLFLOW_TRACKING_URI="http://127.0.0.1:30000"' >> ~/.bashrc
    echo 'export MLFLOW_S3_ENDPOINT_URL="http://127.0.0.1:30001"' >> ~/.bashrc

    minikube addons enable registry
  if ! command kubectl >/dev/null 2>&1; then
    # Install kubectl
    minikube kubectl -- get po -A
  else
    echo "kubectl is already installed"
  fi
}

deploy (){
    minikube kubectl -- create namespace tsops-dev

    if [[ ! -f ../k8s/secrets.yaml ]]; then
      echo "secrets.yaml doesn't exist, creating one by copying secrets_sample.yaml"
      cp "../k8s/secrets_sample.yaml" "../k8s/secrets.yaml"
    fi

    for file in ../k8s/*.yaml; do
      if [[ $file != "../k8s/secrets_sample.yaml" ]]; then
        echo $file
        minikube kubectl -- apply -f "$file"
      fi
    done
}

remove () {
  echo "Removing minikube and assorted tools from $PREFIX"

  rm -f "${PREFIX}/kubectl"
  rm -f "${PREFIX}/minikube"
}

if ! grep -E 'vmx|svm' /proc/cpuinfo > /dev/null; then
  echo "CPU does not support virtualization"
  exit 1
fi

case $CMD in
  install)
    install
    ;;
  start)
    start
    ;;
  deploy)
    deploy
    ;;
  remove)
    remove
    ;;
  *)
    echo "install_minikube.sh [install|start|remove|deploy] <install_prefix>"
    ;;
esac