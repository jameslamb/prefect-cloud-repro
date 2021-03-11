1. Fill out `.env` with the following.

```text
PREFECT_USER_TOKEN=
PREFECT_CLOUD_PROJECT_NAME=
FLOW_NAME=
```

2. Authenticate with Prefect Cloud

```shell
source .env
prefect auth login -t ${PREFECT_USER_TOKEN}
```

3. Delete the testing project (in case it's left over from previous runs), then recreate it

```shell
prefect delete project ${PREFECT_CLOUD_PROJECT_NAME}
prefect create project ${PREFECT_CLOUD_PROJECT_NAME}
```

4. Register the flow using `prefect` 0.13.19 and a KubernetesJobEnvironment

```shell
docker run \
    -v $(pwd):/opt/code \
    -w /opt/code \
    --env-file=.env \
    -it \
    prefecthq/prefect:0.13.19-python3.7 \
    /bin/bash
```

Inside the container:

```shell
prefect auth login -t ${PREFECT_USER_TOKEN}
python register-flow.py
```

5. Start a flow run. This will fail because you're not running an agent, but that doesn't matter. The goal here is just to inspect the flow run object.

```shell
prefect run flow \
    --name ${FLOW_NAME} \
    --project ${PREFECT_CLOUD_PROJECT_NAME}
```

6. This will return some output like the following. Make note of the ID

> Flow Run: https://cloud.prefect.io/prefect-is-perfect/flow-run/6a8c098f-4d35-4c36-b870-fd9b046add0e

```shell
export FLOW_RUN_ID=6a8c098f-4d35-4c36-b870-fd9b046add0e
```

7. Run the following in a Python session to get the details of the flow run.

```python
import os
from prefect import Client

client = Client()

FLOW_RUN_ID = os.environ["FLOW_RUN_ID"]

query = """
    query {
      flow_run_by_pk(id: "%s") {
        id,
        flow {
          id,
          environment
        },
        run_config
      }
    }
""" % FLOW_RUN_ID

client.graphql(query)
```

You should get a response similar to what is shown below. Save that output somewhere, to compare it to output from a later step.

```json
{
    "data": {
        "flow_run_by_pk": {
            "id": "6a8c098f-4d35-4c36-b870-fd9b046add0e",
            "flow": {
                "id": "813db127-85d5-45fd-9633-a621d7035443",
                "environment": {
                    "type": "KubernetesJobEnvironment",
                    "labels": [
                        "2fd60ffa052c"
                    ],
                    "metadata": {
                        "image": "prefecthq/prefect:all_extras-0.13.19"
                    },
                    "__version__": "0.13.19"
                }
            },
            "run_config": null
        }
    }
}
```

8. Exit the `prefect` 0.13.19 container.

```shell
exit
```

9. Enter a new container that has `prefect` 0.14.11, and re-register the flow.

```shell
docker run \
    -v $(pwd):/opt/code \
    -w /opt/code \
    --env-file=.env \
    -it \
    prefecthq/prefect:0.14.11-python3.7 \
    /bin/bash
```

Inside the container, run the following. Note that this time, the new version of the flow will set `flow.run_config = KubernetesRun()`

```shell
prefect auth login -t ${PREFECT_USER_TOKEN}
python register-flow.py
```

10. Check that there are now 2 versions of the flow `some-flow`

```shell
prefect get flows | grep -E "AGE|some-flow"
```

You should see something like this

```text
NAME         VERSION    AGE             ID                                    PROJECT NAME
some-flow    2          1 minute ago    91a89e5f-534c-43f5-a2c4-1fd86e160e84  test-project
```

11. Start a flow run. Once again, it doesn't matter that you don't have any agents running and that the flow will fail.

```shell
prefect run flow \
    --name ${FLOW_NAME} \
    --project ${PREFECT_CLOUD_PROJECT_NAME}
```

12. This will return some output like the following. Make note of the ID

> Flow Run: https://cloud.prefect.io/prefect-is-perfect/flow-run/ccd896c4-2d95-4e64-b066-d859673b370a

```shell
export FLOW_RUN_ID=ccd896c4-2d95-4e64-b066-d859673b370a
```

13. Run the following in a Python session to get the details of the flow run.

```python
import os
from prefect import Client

client = Client()

FLOW_RUN_ID = os.environ["FLOW_RUN_ID"]

query = """
    query {
      flow_run_by_pk(id: "%s") {
        id,
        flow {
          id,
          environment
        },
        run_config
      }
    }
""" % FLOW_RUN_ID

client.graphql(query)
```

You should get a response similar to what is shown below. Note that `run_config` is now populated and `environment` is null.

```json
{
    "data": {
        "flow_run_by_pk": {
            "id": "ccd896c4-2d95-4e64-b066-d859673b370a",
            "flow": {
                "id": "91a89e5f-534c-43f5-a2c4-1fd86e160e84",
                "environment": null
            },
            "run_config": {
                "env": null,
                "type": "KubernetesRun",
                "image": null,
                "labels": [
                    "40d8e489be91"
                ],
                "cpu_limit": null,
                "__version__": "0.14.11",
                "cpu_request": null,
                "job_template": null,
                "memory_limit": null,
                "memory_request": null,
                "job_template_path": null,
                "image_pull_secrets": null,
                "service_account_name": null
            }
        }
    }
}

```

14. exit this container

```shell
exit
```

15. run a new `prefect` 0.13.19 container, repeating some of the steps above

```shell
docker run \
    -v $(pwd):/opt/code \
    -w /opt/code \
    --env-file=.env \
    -it \
    prefecthq/prefect:0.13.19-python3.7 \
    /bin/bash
```

in the container:

```shell
prefect auth login -t ${PREFECT_USER_TOKEN}
python register-flow.py

echo "checking that the flow is on version 3"
prefect get flows | grep -E "AGE|some-flow"

prefect run flow \
    --name ${FLOW_NAME} \
    --project ${PREFECT_CLOUD_PROJECT_NAME}
```

16. store the ID of the flow run, and check for the flow run details again

```shell
export FLOW_RUN_ID=98cf5520-8d5b-45ae-af9c-2d18f8675f5a
```

```python
import os
from prefect import Client

client = Client()

FLOW_RUN_ID = os.environ["FLOW_RUN_ID"]

query = """
    query {
      flow_run_by_pk(id: "%s") {
        id,
        flow {
          id,
          environment
        },
        run_config
      }
    }
""" % FLOW_RUN_ID

client.graphql(query)
```

You should see that the flow run has now switched back from run_config to environment. Ok, still doing what we'd expect.

```json
{
    "data": {
        "flow_run_by_pk": {
            "id": "98cf5520-8d5b-45ae-af9c-2d18f8675f5a",
            "flow": {
                "id": "2053cb44-d1eb-4579-9ff1-4e59f2198163",
                "environment": {
                    "type": "KubernetesJobEnvironment",
                    "labels": [
                        "2982b8d0aa57"
                    ],
                    "metadata": {
                        "image": "prefecthq/prefect:all_extras-0.13.19"
                    },
                    "__version__": "0.13.19"
                }
            },
            "run_config": null
        }
    }
}
```

17. Exit the container

```shell
exit
```

18. Try starting with a flow that has `KubernetesRun` FIRST, then switching it to `KubernetesJobEnvironment`.

clean out all the old flows

```shell
source .env
prefect delete project ${PREFECT_CLOUD_PROJECT_NAME}
prefect create project ${PREFECT_CLOUD_PROJECT_NAME}
```

```shell
docker run \
    -v $(pwd):/opt/code \
    -w /opt/code \
    --env-file=.env \
    -it \
    prefecthq/prefect:0.14.11-python3.7 \
    /bin/bash
```

in the container:

```shell
prefect auth login -t ${PREFECT_USER_TOKEN}
python register-flow.py

echo "checking that the flow is on version 1"
prefect get flows | grep -E "AGE|some-flow"

prefect run flow \
    --name ${FLOW_NAME} \
    --project ${PREFECT_CLOUD_PROJECT_NAME}
```

19. store the ID of the flow run, and check for the flow run details again

```shell
export FLOW_RUN_ID=7900e87e-ee0f-4597-a923-23888a94c735
```

In a Python session:

```python
import os
from prefect import Client

client = Client()

FLOW_RUN_ID = os.environ["FLOW_RUN_ID"]

query = """
    query {
      flow_run_by_pk(id: "%s") {
        id,
        flow {
          id,
          environment
        },
        run_config
      }
    }
""" % FLOW_RUN_ID

client.graphql(query)
```

You should see that the flow run has a run_config with a `KubernetesRun`, and `flow.environment` is null.

```json
{
    "data": {
        "flow_run_by_pk": {
            "id": "7900e87e-ee0f-4597-a923-23888a94c735",
            "flow": {
                "id": "951f14bf-9cc1-40bf-8c3f-21fca751f24c",
                "environment": null
            },
            "run_config": {
                "env": null,
                "type": "KubernetesRun",
                "image": null,
                "labels": [
                    "5182fc63bc4c"
                ],
                "cpu_limit": null,
                "__version__": "0.14.11",
                "cpu_request": null,
                "job_template": null,
                "memory_limit": null,
                "memory_request": null,
                "job_template_path": null,
                "image_pull_secrets": null,
                "service_account_name": null
            }
        }
    }
}
```

20. Exit the container

```shell
exit
```

21. Using a `prefect` 0.13.19 container, try registering the flow using `KubernetesJobEnvironment`

```shell
docker run \
    -v $(pwd):/opt/code \
    -w /opt/code \
    --env-file=.env \
    -it \
    prefecthq/prefect:0.13.19-python3.7 \
    /bin/bash
```

in the container:

```shell
prefect auth login -t ${PREFECT_USER_TOKEN}
python register-flow.py

echo "checking that the flow is on version 2"
prefect get flows | grep -E "AGE|some-flow"

prefect run flow \
    --name ${FLOW_NAME} \
    --project ${PREFECT_CLOUD_PROJECT_NAME}
```

21. store the ID of the flow run, and check for the flow run details again

```shell
export FLOW_RUN_ID=7a77056b-0bcf-4443-aff3-0ecc04ee622a
```

In a Python session:

```python
import os
from prefect import Client

client = Client()

FLOW_RUN_ID = os.environ["FLOW_RUN_ID"]

query = """
    query {
      flow_run_by_pk(id: "%s") {
        id,
        flow {
          id,
          environment
        },
        run_config
      }
    }
""" % FLOW_RUN_ID

client.graphql(query)
```

You should see that the flow run has a run_config with a `KubernetesRun`, and `flow.environment` is null.

```json
{
    "data": {
        "flow_run_by_pk": {
            "id": "7a77056b-0bcf-4443-aff3-0ecc04ee622a",
            "flow": {
                "id": "6dddd60b-9a69-477a-a04e-9c55ed3a4d32",
                "environment": {
                    "type": "KubernetesJobEnvironment",
                    "labels": [
                        "cccaa0e83cb8"
                    ],
                    "metadata": {
                        "image": "prefecthq/prefect:all_extras-0.13.19"
                    },
                    "__version__": "0.13.19"
                }
            },
            "run_config": null
        }
    }
}
```
