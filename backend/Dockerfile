FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements.txt mangum

# Copy application code
COPY main.py models.py database.py ${LAMBDA_TASK_ROOT}/

# Override the default CMD with the handler
CMD ["main.handler"]
