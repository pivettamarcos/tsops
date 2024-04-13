all() {
  build
  push
  serve
}

build(){
  echo $RUN_UUID
  mlflow models build-docker -m runs:/${RUN_UUID}/model -n localhost:5000/${MODEL_NAME}-infer:${RUN_NAME} --enable-mlserver 
}

push(){
  kubectl port-forward --namespace kube-system service/registry 5000:80 &
  PORT_FORWARD_PID=$!

  docker run --rm -d --network=host --name socat alpine ash -c "apk add socat && socat TCP-LISTEN:5000,reuseaddr,fork TCP:host.docker.internal:5000" &

  sleep 5

  docker push localhost:5000/${MODEL_NAME}-infer:${RUN_NAME}

  kill $PORT_FORWARD_PID
  docker stop socat
}

serve(){
FILE="${SCRIPT_DIR}/../k8s/${PROJECT_NAME}.yaml"

echo ${MODEL_NAME//./_}-infer

cat << EOF > "${SCRIPT_DIR}/${PROJECT_NAME}_inference_service_temp.yaml"
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: ${MODEL_NAME//./-}-infer
  namespace: tsops-dev
spec:
  predictor:
    containers:
      - name: ${MODEL_NAME//./-}-infer
        image: "10.110.245.161:80/${MODEL_NAME}-infer:${RUN_NAME}"
        ports:
          - containerPort: 8080
            protocol: TCP
        env:
          - name: PROTOCOL
            value: "v2"
EOF


  kubectl apply -f "${SCRIPT_DIR}/${PROJECT_NAME}_inference_service_temp.yaml"
  INGRESS_GATEWAY_SERVICE=$(kubectl get svc -n istio-system --selector="app=istio-ingressgateway" -o jsonpath='{.items[0].metadata.name}')
  kubectl port-forward -n istio-system svc/${INGRESS_GATEWAY_SERVICE} 8080:80
}


POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--project_name)
      PROJECT_NAME="$2"
      shift # past argument
      shift # past value
      ;;
    -m|--model_name_alias)
      MODEL_NAME_ALIAS="$2"
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

if [ -z "$MODEL_NAME_ALIAS" ]
then
  echo "Error: No MLFlow model name supplied"
  exit 1
fi

echo "PROJECT_NAME = ${PROJECT_NAME}"
echo "MODEL_NAME_ALIAS   = ${MODEL_NAME_ALIAS}"

SCRIPT_DIR=$(dirname "$0")
PROJECT_DIR="$SCRIPT_DIR/../notebooks/mlflow_projects/$PROJECT_NAME"
COMMIT_HASH=$(git rev-parse --short HEAD)

read MODEL_NAME RUN_NAME RUN_UUID <<< $(python3 << END
from mlflow import MlflowClient

client = MlflowClient()
name, alias = "${MODEL_NAME_ALIAS}".split("@")
run_id = client.get_model_version_by_alias(name, alias).run_id
run_name = client.get_run(run_id).info.run_name
run_uuid = client.get_run(run_id).info.run_uuid
print(name, run_name, run_uuid)
END
)

case $1 in
  build)
    build
    ;;
  push)
    push
    ;;
  serve)
    serve
    ;;
  *)
    echo "Format is serve.sh [build|push|serve|all] --project_name <project_name> --model_name_alias <model_name@alias>"
    exit 1
    ;;
esac