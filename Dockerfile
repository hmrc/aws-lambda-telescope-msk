FROM public.ecr.aws/lambda/python:3.14

RUN yum install ca-certificates -y

COPY requirements.txt requirements-tests.txt ${LAMBDA_TASK_ROOT}/

RUN PIP_INDEX_URL="${PIP_INDEX_URL}" \
    python -m venv venv && \
    source ./venv/bin/activate && \
    pip install --requirement requirements-tests.txt --target "${LAMBDA_TASK_ROOT}"

COPY src tests ${LAMBDA_TASK_ROOT}/

CMD [ "handler.lambda_handler" ]
