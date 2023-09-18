# ML-Training-Pipeline
This project illustrates a Machine-Learning training pipeline. The main focus is the MLOps Practices like Workflow Orchestration, CICD, Experiment tracking, Model versioning.
![image](https://github.com/Abd-elr4hman/ML-Training-Pipeline/assets/87248009/c43d2939-71f5-4175-8698-2d866f1105e5)




the project is split into 3 repositories:
* Processing job repo: [here](https://github.com/Abd-elr4hman/ProcessingJob).
* Training job repo: [here](https://github.com/Abd-elr4hman/TrainingJob)
* Orchestration repo: This one.
# To Do:
### Data Processing:
* [x] Process MNIST Raw dataset.
* [x] Define a SageMaker Processing Job.
* [x] Build a docker container to use with SageMaker,
* [x] Automate testing, building and pushing docker container to AWS ECR with github workflows.
### Model Training:
* [x] Use Tensorflow to train Mnist classification model.
* [x] Create a SageMaker Training Job using SageMaker Tensorflow deeplearning container.
### Experiment Tracking, Model versioning:
* [x] Perform Experiment tracking, model logging with MLflow, RDS Postgres db and S3.
### Orchestration:
* [x] Orchestrate the training process with AWS Step-functions.
