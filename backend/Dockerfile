FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py models.py database.py ${LAMBDA_TASK_ROOT}/

# Install Mangum for Lambda adapter
RUN pip install --no-cache-dir mangum

# Create Lambda handler wrapper
RUN echo 'from mangum import Mangum\nfrom main import app\nhandler = Mangum(app)' > ${LAMBDA_TASK_ROOT}/lambda_handler.py

# Set the CMD to your handler
CMD ["lambda_handler.handler"]
