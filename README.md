# tsops
A deployable stack for training and online inference of time series models

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