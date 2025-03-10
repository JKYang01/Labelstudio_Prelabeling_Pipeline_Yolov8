#!/bin/bash

# Default values
SAVE_PIECE=false # default false, cropping annotation gonna upgrade in the future with database interaction
TILE_SIZE=640
BUCKET_NAME="labelstudiocloudtest"
INPUT_PATH="wenzhe_test/"    # the folder path of .png files, wenzhe_test/
OUTPUT_PATH=""   # leave it blank
S3_MODEL_PATH="s3://sagemaker-us-east-1-100328509916/output_shapes_gen3_dillonchris_feb2025_batch8_1800_85epochs_2025-02-27-21-47-24/train/weights/best.pt"  # put the annotataion model's s3 url
TASK_NAME="shape_ann"
IMPORT_BUCKET_NAME="labelstudiocloudtest"
API_KEY=""
URL="https://app.humansignal.com/"
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_REGION="us-east-1"

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

# Run the Python script
python run.py --config config.json

