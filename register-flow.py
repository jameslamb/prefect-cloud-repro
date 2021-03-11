import os
import prefect
from prefect import Flow, task

FLOW_NAME = os.environ["FLOW_NAME"]
PROJECT_NAME = os.environ["PREFECT_CLOUD_PROJECT_NAME"]

@task
def do_something() -> str:
    return "no"

with Flow(name=FLOW_NAME) as flow:
    x = do_something()


if prefect.__version__.startswith("0.13"):
    print("Using KubernetesJobEnvironment")
    from prefect.environments import KubernetesJobEnvironment
    flow.environment = KubernetesJobEnvironment()
else:
    from prefect.run_configs import KubernetesRun  # noqa: F401
    print("Using KubernetesRun")
    flow.run_config = KubernetesRun()

flow.register(project_name=PROJECT_NAME)
