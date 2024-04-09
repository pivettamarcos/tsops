#!/bin/bash

CMD=${1:-install}
PREFIX=${2:-/usr/local/bin/}

install () {
  echo "Attempting to install minikube and assorted tools to $PREFIX"

  if ! command minikube >/dev/null 2>&1; then
    curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    chmod +x minikube
    mv minikube "$PREFIX"
  else
    echo "minikube is already installed"
  fi
}

start (){
    echo "Enter number of cpu cores"
	read CPU
	echo "Enter memory in MB"
    read MEMORY
    echo "Starting minikube..."
    minikube start --cpus $CPU --memory $MEMORY

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