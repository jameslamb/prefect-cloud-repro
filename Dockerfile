ARG PREFECT_VERSION
FROM prefecthq/prefect:${PREFECT_VERSION}-python3.7

ARG CODE_DIR="/opt/saturn-prefect-agent"

COPY register-flow.py .
RUN python register-flow.py
