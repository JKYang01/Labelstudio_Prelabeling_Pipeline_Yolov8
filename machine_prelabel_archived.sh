#!/bin/bash

# Default values
SAVE_PIECE=false # default false, cropping annotation gonna upgrade in the future with database interaction
TILE_SIZE=640
BUCKET_NAME="labelstudiocloudtest"
INPUT_PATH=""    # the folder path of .png files like wenzhe_test/
OUTPUT_PATH=""   # leave it blank
S3_MODEL_PATH=""  # put the annotataion model's s3 url
TASK_NAME="shape_ann"
IMPORT_BUCKET_NAME="labelstudiocloudtest"
API_KEY=""
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_REGION="us-east-1"



python run.py \
  --save_piece=$SAVE_PIECE \
  --tile_size=$TILE_SIZE \
  --bucket_name=$BUCKET_NAME \
  --input_path=$INPUT_PATH \
  --output_path=$OUTPUT_PATH \
  --s3_model_path=$S3_MODEL_PATH \
  --task_name=$TASK_NAME \
  --import_bucket_name=$IMPORT_BUCKET_NAME \
  --url=$URL \
  --api_key=$API_KEY \
  --aws_access_key_id=$AWS_ACCESS_KEY_ID \
  --aws_secret_access_key=$AWS_SECRET_ACCESS_KEY \
  --aws_region=$AWS_REGION


## Parse command line arguments
#while [[ $# -gt 0 ]]; do
#  case $1 in
#    --save_piece=*)
#      SAVE_PIECE="${1#*=}"
#      shift
#      ;;
#    --tile_size=*)
#      TILE_SIZE="${1#*=}"
#      shift
#      ;;
#    --bucket_name=*)
#      BUCKET_NAME="${1#*=}"
#      shift
#  .....
