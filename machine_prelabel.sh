#!/bin/bash

# Default values
SAVE_PIECE=false # default false, cropping annotation gonna upgrade in the future with database interaction
TILE_SIZE=640
BUCKET_NAME="labelstudiocloudtest"
INPUT_PATH=""
OUTPUT_PATH=""
TASK_NAME="shape_ann"
IMPORT_BUCKET_NAME="labelstudiocloudtest"
API_KEY=""
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_REGION="us-east-1"


# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --save_piece=*)
      SAVE_PIECE="${1#*=}"
      shift
      ;;
    --tile_size=*)
      TILE_SIZE="${1#*=}"
      shift
      ;;
    --bucket_name=*)
      BUCKET_NAME="${1#*=}"
      shift
      ;;
    --input_path=*)
      INPUT_PATH="${1#*=}"
      shift
      ;;
    --output_path=*)
      OUTPUT_PATH="${1#*=}"
      shift
      ;;
    --task_name=*)
      TASK_NAME="${1#*=}"
      shift
      ;;
    --import_bucket_name=*)
      IMPORT_BUCKET_NAME="${1#*=}"
      shift
      ;;
    --url=*)
      URL="${1#*=}"
      shift
      ;;
    --api_key=*)
      API_KEY="${1#*=}"
      shift
      ;;
    --aws_access_key_id=*)
      AWS_ACCESS_KEY_ID="${1#*=}"
      shift
      ;;
    --aws_secret_access_key=*)
      AWS_SECRET_ACCESS_KEY="${1#*=}"
      shift
      ;;
    --aws_region=*)
      AWS_REGION="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown parameter: $1"
      exit 1
      ;;
  esac
done

# Export variables as environment variables
export SAVE_PIECE=$SAVE_PIECE
export TILE_SIZE=$TILE_SIZE
export BUCKET_NAME=$BUCKET_NAME
export INPUT_PATH=$INPUT_PATH
export OUTPUT_PATH=$OUTPUT_PATH
export TASK_NAME=$TASK_NAME
export IMPORT_BUCKET_NAME=$IMPORT_BUCKET_NAME
export URL=$URL
export API_KEY=$API_KEY
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
export AWS_REGION=$AWS_REGION
# Run the Python script
python run.py