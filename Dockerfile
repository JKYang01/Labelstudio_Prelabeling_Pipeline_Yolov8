FROM public.ecr.aws/lambda/python:3.12

# Set environment variables
# Prevents Python from creating .pyc files, for cleaner container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies including Tesseract OCR
RUN yum update -y && \
    yum install -y amazon-linux-extras && \
    amazon-linux-extras enable epel && \
    yum install -y epel-release && \
    yum install -y tesseract-ocr && \
    yum clean all \

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    export PATH="/opt/poetry/bin:$PATH" && \
    poetry config virtualenvs.create false

# Add Poetry to the PATH for all subsequent steps
ENV PATH="/opt/poetry/bin:$PATH"

# Set the working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy pyproject.toml and poetry.lock
COPY pdf_piece/pyproject.toml poetry.lock ${LAMBDA_TASK_ROOT}
RUN poetry install --without dev --no-interaction --no-ansi

COPY ./database ${LAMBDA_TASK_ROOT}/database

# Command to run your application
# CMD ["poetry", "run", "python", "your_main_script.py"]
CMD ["database.test_db_connect.lambda_handler"]
