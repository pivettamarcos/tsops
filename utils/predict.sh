predict (){
    SERVICE_HOSTNAME=$(kubectl get inferenceservice ${MODEL_NAME//./-}-infer -n tsops-dev -o jsonpath='{.status.url}' | cut -d "/" -f 3)
    curl -v \
    -H "Host: ${SERVICE_HOSTNAME}" \
    -H "Content-Type: application/json" \
    -d @./${INPUT_FILE} \
    http://localhost:8080/v2/models/mlflow-model/infer
}

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--model_name)
      MODEL_NAME="$2"
      shift # past argument
      shift # past value
      ;;
    -i|--input_file)
      INPUT_FILE="$2"
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


if [ -z "$MODEL_NAME" ]
then
  echo "Error: No project name supplied"
  exit 1
fi

if [ -z "$INPUT_FILE" ]
then
  echo "Input file not provided"
  exit 1
fi

echo "PROJECT_NAME = ${PROJECT_NAME}"

SCRIPT_DIR=$(dirname "$0")
PROJECT_DIR="$SCRIPT_DIR/../notebooks/mlflow_projects/$PROJECT_NAME"
COMMIT_HASH=$(git rev-parse --short HEAD)

case $1 in
  predict)
    predict
    ;;
  *)
    echo "Format is predict.sh [predict] --model_name <model_name> --input_file <input_file>"
    exit 1
    ;;
esac