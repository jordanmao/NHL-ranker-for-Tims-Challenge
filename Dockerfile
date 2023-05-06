FROM public.ecr.aws/lambda/python:3.9

# dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# source code
COPY autopicker/ "${LAMBDA_TASK_ROOT}/autopicker/"
COPY aws_lambda_handler/app.py "${LAMBDA_TASK_ROOT}"

CMD [ "app.lambda_handler" ]
