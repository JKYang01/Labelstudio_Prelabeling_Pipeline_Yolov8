#!/bin/bash

# Get parameters from environment variables or use defaults
SAVE_PIECE=${SAVE_PIECE:-false}
TILE_SIZE=${TILE_SIZE:-640}
BUCKET_NAME=${BUCKET_NAME:-"labelstudiocloudtest"}
INPUT_PATH=${INPUT_PATH:-"wenzhe_test/"}
OUTPUT_PATH=${OUTPUT_PATH:-""}
S3_MODEL_PATH=${S3_MODEL_PATH:-""}
TASK_NAME=${TASK_NAME:-"shape_ann"}
IMPORT_BUCKET_NAME=${IMPORT_BUCKET_NAME:-"labelstudiocloudtest"}
API_KEY=${API_KEY:-""}
URL=${URL:-"https://app.humansignal.com/"}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-""}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-""}
AWS_REGION=${AWS_REGION:-"us-east-1"}

# Create a JSON config file
cat > config.json << EOF
{
  "overrides": {
    "save_piece": ${SAVE_PIECE},
    "tile_size": ${TILE_SIZE},
    "bucket_name": "${BUCKET_NAME}",
    "input_path": "${INPUT_PATH}",
    "output_path": "${OUTPUT_PATH}",
    "s3_model_path": "${S3_MODEL_PATH}",
    "task_name": "${TASK_NAME}"
  },
  "credential": {
    "import_bucket_name": "${IMPORT_BUCKET_NAME}",
    "prefix": "${INPUT_PATH}ml_predictions/ann/${TASK_NAME}",
    "URL": "${URL}",
    "API_KEY": "${API_KEY}",
    "aws_access_key_id": "${AWS_ACCESS_KEY_ID}",
    "aws_secret_access_key": "${AWS_SECRET_ACCESS_KEY}",
    "region_name": "${AWS_REGION}"
  }
}
EOF

# Log the configuration (hide sensitive information)
echo "Running with configuration:"
cat config.json | sed 's/"aws_secret_access_key": "[^"]*"/"aws_secret_access_key": "***"/g' | \
    sed 's/"API_KEY": "[^"]*"/"API_KEY": "***"/g' | \
    sed 's/"aws_access_key_id": "[^"]*"/"aws_access_key_id": "***"/g'
# Run the Python script
python run.py --config config.json