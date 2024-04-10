# tsops
A deployable stack for training and online inference of time series models

## How to deploy

1. Deploy 

    To deploy with **minikube**, run ``cd utils; ./install-deploy-miniube.sh **install | start | deploy**``
2. To **train** model
    - With virtualenv dependencies:

        ``cd`` to an MlFlow project and ``mlflow run <project_uri> --env-manager virtualenv``

    - *With kubernetes backend (broken in minikube)*:

        ``` mlflow run <project_uri> --backend kubernetes --backend-config <kubernetes_config.json> ```
3. To **serve** a model:
    - Locally:

        ``cd`` to an Mlflow project and ``mlflow models serve -m runs:/runID/model -p <serving_port> --enable-mlserver``
    - In emulated cluster (minikube or sorts):
        1. Create an InferenceService named <YOUR_CONFIG_FILE.yaml>:
            ```
            apiVersion: "serving.kserve.io/v1beta1"
            kind: "InferenceService"
            metadata:
                name: "<inference-service-name>"
                namespace: "<namespace-name>"
            spec:
            predictor:
                serviceAccountName: sa
                model:
                    modelFormat:
                        name: mlflow
                    protocolVersion: v2
                    storageUri: "<s3_uri>"
            ```
        2. ``kubectl apply -f <YOUR_CONFIG_FILE.yaml>``
        3. Port forward istio service
            ```
            INGRESS_GATEWAY_SERVICE=$(kubectl get svc -n <namespace-name> --selector="app=istio-ingressgateway" -o jsonpath='{.items[0].metadata.name}')
            kubectl port-forward -n <namespace-name> svc/${INGRESS_GATEWAY_SERVICE} <serving_port>:80
            ```
4. To **inference** a model:
    - Locally:

        ``` curl -X POST -H "Content-Type:application/json" --data '{"inputs": [[14.23, 1.71, 2.43, 15.6, 127.0, 2.8, 3.06, 0.28, 2.29, 5.64, 1.04, 3.92, 1065.0]]' http://127.0.0.1:<serving_port>/invocations ```
    - In emulated cluster (minikube or sorts):

        ```
        curl -v \
        -H "Host: ${SERVICE_HOSTNAME}" \
        -H "Content-Type: application/json" \
        -d @./test-input.json \
        http://localhost:<serving_port>/v2/models/<inference-service-name>/infer
        ```

## Stack components

- [ ] CI/CD of application
- [ ] Time Series database
- [ ] Feature store
- [ ] Model tracking (MLflow)
- [ ] Scheduling (AirFlow)
- [ ] Model monitoring

## MLOps Maturity level

> Current level: **0**

See : [Azure Machine Learning
](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model)

| Level | Description | Highlights | Technology |
|-------|-------------|------------|------------|
| 0 | No MLOps | Difficult to manage full machine learning model lifecycle<br>The teams are disparate and releases are painful<br>Most systems exist as "black boxes," little feedback during/post deployment | <br>Manual builds and deployments<br>Manual testing of model and application<br>No centralized tracking of model performance<br>Training of model is manual |
| 1 | DevOps but no MLOps | Releases are less painful than No MLOps, but rely on Data Team for every new model<br>Still limited feedback on how well a model performs in production<br>Difficult to trace/reproduce results | <br>Automated builds<br>Automated tests for application code |
| 2 | Automated Training | Training environment is fully managed and traceable<br>Easy to reproduce model<br>Releases are manual, but low friction | <br>Automated model training<br>Centralized tracking of model training performance<br>Model management |
| 3 | Automated Model Deployment | Releases are low friction and automatic<br>Full traceability from deployment back to original data<br>Entire environment managed: train > test > production | <br>Integrated A/B testing of model performance for deployment<br>Automated tests for all code<br>Centralized tracking of model training performance |
| 4 | Full MLOps Automated Operations | Full system automated and easily monitored<br>Production systems are providing information on how to improve and, in some cases, automatically improve with new models<br>Approaching a zero-downtime system | <br>Automated model training and testing<br>Verbose, centralized metrics from deployed model |