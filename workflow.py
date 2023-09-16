import logging

import sagemaker
from sagemaker.tensorflow import TensorFlow

import stepfunctions
from stepfunctions.workflow import Workflow
from stepfunctions import steps
from stepfunctions.inputs import ExecutionInput
from stepfunctions.workflow import Workflow

from sagemaker.processing import Processor, ProcessingInput, ProcessingOutput
from datetime import datetime

stepfunctions.set_stream_logger(level=logging.INFO)

sagemaker_session = sagemaker.Session()
region = sagemaker_session.boto_session.region_name


# define global constants
PROCESSING_IMAGE_URI = "401082536487.dkr.ecr.eu-central-1.amazonaws.com/mnist-processingjob:889d1e4cd1e9f06a67a9ba92c0cb4f6112202ba4"
PROCESSING_INPUT = "s3://training-data-sagemaker-tensorflow-mnist/processing_input/"
PROCESSING_OUTPUT = "s3://training-data-sagemaker-tensorflow-mnist/processing_output"
TRAINING_OUTPUT = "s3://training-data-sagemaker-tensorflow-mnist/training_output"


PROCESSING_INSTANCE_TYPE = "ml.t3.large"
TRAINING_INSTANCE_TYPE = "ml.m5.large"

EXECUTION_ROLE = "arn:aws:iam::401082536487:role/AWS-SAGEMAKER-EXECUTION"
WORKFLOW_EXECUTION_ROLE = "arn:aws:iam::401082536487:role/AmazonSageMaker-StepFunctionsWorkflowExecutionRole"

# define stepfunctions workflow execution input
execution_input = ExecutionInput(
    schema={
        "TrainingJobName": str,
        "PreprocessingJobName": str,
    }
)

    
# create processing step
def create_process_step() -> stepfunctions.steps.ProcessingStep:
    """
    create process step
    """
    processor = Processor(image_uri=PROCESSING_IMAGE_URI,
                    role=EXECUTION_ROLE,
                    instance_count=1,
                    instance_type=PROCESSING_INSTANCE_TYPE)
    
    step_process = stepfunctions.steps.ProcessingStep(
        state_id="Preprocessing Data",
        processor=processor,
        job_name=execution_input["PreprocessingJobName"],
        inputs=[ProcessingInput(input_name= "processing_input",source=PROCESSING_INPUT, destination="/opt/ml/processing/input")],
        outputs=[
                ProcessingOutput(output_name="processing_output", source="/opt/ml/processing/output", destination=PROCESSING_OUTPUT),
            ],
    )
    return step_process

# create a training step
def create_training_step():
    """
    create a training step
    """
    mnist_estimator = TensorFlow(
        entry_point="mnist_training.py",
        role=EXECUTION_ROLE,
        instance_count=1,
        instance_type=TRAINING_INSTANCE_TYPE,
        framework_version="2.7",
        py_version="py38",
        source_dir= "src",
        output_path= TRAINING_OUTPUT

    )
    
    training_step = steps.TrainingStep(
        "Model Training",
        estimator=mnist_estimator,
        data={
            "train":PROCESSING_OUTPUT
        },
        job_name=execution_input["TrainingJobName"],
        wait_for_completion=True,
    )
    return training_step

def create_workflow():
    """
    create a state machine for ml pipeline
    """
    
    # processing step
    processing_step = create_process_step()
    
    # training step
    training_step = create_training_step()
    
    # workflow
    workflow_definition = steps.Chain(
        [processing_step, training_step]
    )
    
    workflow = Workflow(
        name="TrainingWorkflow",
        definition=workflow_definition,
        role=WORKFLOW_EXECUTION_ROLE,
        execution_input=execution_input,
    )
    
    return workflow

if __name__ == "__main__":
    mnist_workflow = create_workflow()
    mnist_workflow.render_graph()
    mnist_workflow.create()

    # datetime object containing current date and time
    now = datetime.now()

    # dd-mm-YY-H-M-S
    dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
    print("date and time =", dt_string)


    execution = mnist_workflow.execute(
        inputs={
            "TrainingJobName": f"mnist-tensorflow-training-{dt_string}",  # Each Sagemaker Job requires a unique name,
            "PreprocessingJobName": f"mnist-tensorflow-processing-{dt_string}",  # Each Sagemaker Job requires a unique name,
        }
    )

    execution.render_progress()



