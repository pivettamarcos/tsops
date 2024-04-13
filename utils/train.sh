all() {
  build
  push
  train
}

build(){
  docker build $PROJECT_DIR -t localhost:5000/$PROJECT_NAME-train:$COMMIT_HASH
}

push(){
  kubectl port-forward --namespace kube-system service/registry 5000:80 &
  PORT_FORWARD_PID=$!

  docker run --rm -d --network=host --name socat alpine ash -c "apk add socat && socat TCP-LISTEN:5000,reuseaddr,fork TCP:host.docker.internal:5000" &

  sleep 5
  docker push localhost:5000/$PROJECT_NAME-train:$COMMIT_HASH

  kill $PORT_FORWARD_PID
  docker stop socat
}

train(){
  kubectl port-forward --namespace kube-system service/registry 5000:80 &
  PORT_FORWARD_PID=$!

  docker run --rm -d --network=host --name socat alpine ash -c "apk add socat && socat TCP-LISTEN:5000,reuseaddr,fork TCP:host.docker.internal:5000" &

  sleep 5
  cd $PROJECT_DIR
  cp MLproject MLproject.bak
  yq e ".docker_env.image += \":$COMMIT_HASH\"" -i MLproject
  mlflow run . --backend kubernetes --backend-config kubernetes_config.json 
  mv MLproject.bak MLproject
  cd -

  kill $PORT_FORWARD_PID
  docker stop socat
}

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--project_name)
      PROJECT_NAME="$2"
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters


if [ -z "$PROJECT_NAME" ]
then
  echo "Error: No project name supplied"
  exit 1
fi

echo "PROJECT_NAME = ${PROJECT_NAME}"

SCRIPT_DIR=$(dirname "$0")
PROJECT_DIR="$SCRIPT_DIR/../notebooks/mlflow_projects/$PROJECT_NAME"
COMMIT_HASH=$(git rev-parse --short HEAD)

case $1 in
  build)
    build
    ;;
  push)
    push
    ;;
  train)
    train
    ;;
  all)
    all
    ;;
  *)
    echo "Format is train.sh [build|push|train|all] --project_name <project_name>"
    exit 1
    ;;
esac