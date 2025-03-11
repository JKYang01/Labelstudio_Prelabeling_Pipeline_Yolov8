# ML_Prelabeling_Pipeline
Pre-lableing pipeline interacting with Labelstudio
The following area the parameters that are used in the pipeline
### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| SAVE_PIECE | Whether to save cropped pieces | false |
| TILE_SIZE | Size of image tiles | 640 |
| BUCKET_NAME | S3 bucket name for input/output | labelstudiocloudtest |
| INPUT_PATH | Folder path of .png files | wenzhe_test/ |
| OUTPUT_PATH | Output path | "" |
| S3_MODEL_PATH | Annotation model's S3 URL | "" |
| TASK_NAME | Name of the task | shape_ann |
| IMPORT_BUCKET_NAME | Import bucket name | labelstudiocloudtest |
| API_KEY | API key for the service | "" |
| URL | Service URL | https://app.humansignal.com/ |
| AWS_ACCESS_KEY_ID | AWS access key ID | "" |
| AWS_SECRET_ACCESS_KEY | AWS secret access key | "" |
| AWS_REGION | AWS region | us-east-1 |


## Local environment deploy
install package using Poetry  * recommend method to avoid potential pacakge confiliction
Install Poery https://python-poetry.org/docs/

or use traditional pip method run following:

`$ pip install -r requirement.txt`


open machine_prelabel_config.sh fill in the parameters for your annotation task
If you test on the startcloud, the `URL='https://app.humansignal.com/'` open the account settings and get the labelstuio API key \
if test on your localhost label studio:`URL='http://localhost:8080'` open the account settings and get label studio API key


Then run grand the execution permission to this shell file 

`$ chmod +x machine_prelabel_config.sh`

start run pre-annotation pipeline 

`$ bash machine_prelabel_config.sh`

check the platform, the new project should be there


## Docker Deployment
This repository contains a dockerized ML pipeline for image annotation.

### Quick Start
#### Prerequisites
Docker and Docker Compose installed \
AWS credentials (if using S3) \
API key for Human Signal (if applicable)

#### Setup

Clone this repository:
``` git clone <repository-url>
cd Labelstudio_Prelabeling_Pipeline_YoloV8
```

Create an .env file from the template: * important * \
```
cp .env-example .env
```

Edit the .env file with your specific configuration parameters.

Running with Docker Compose
Start the pipeline with:
```
docker-compose up
```

Or run it in the background:
```angular2html
docker-compose up -d
```

#### (Option) Running with Docker directly
If you don' use docker-compose method, or have problem with running docker compose,\
try to build the image directly with docker with add-in parameters 
Build the image:
```angular2html
docker build -t ml_preann_pipeline .
```

Run the container with your configuration:
```
 docker run --rm \
  -e SAVE_PIECE=false \
  -e TILE_SIZE=640 \
  -e BUCKET_NAME=your_bucket \
  -e INPUT_PATH=your_path/ \
  -e S3_MODEL_PATH=your_model_path \
  -e TASK_NAME=your_task \
  -e API_KEY=your_api_key \
  -e AWS_ACCESS_KEY_ID=your_access_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key \
  ml_pipeline
 ```

## Update Project 
If you have a new annotation project to run and need to change the config parameters
there are 3 ways to achive your goal without rebuild the docker contianer.
1. Using environment variables with docker run:
```
  docker run --rm \
  -e BUCKET_NAME=new-bucket-name \
  -e INPUT_PATH=new-path/ \
  -e TASK_NAME=new-annotation-task \
  your-image-name 
 ```
2. **recommend** Modifying the .env file (if using docker-compose):\
Edit your .env file with the new configuration values
Run `docker-compose up` again (no rebuild needed)


3. Directly editing docker-compose.yml:
Update the environment variables in your docker-compose.yml file
Run `docker-compose up` again

## Development
To modify the pipeline, you can: 
1. Mount your local code into the container by uncommenting the volumes section in docker-compose.yml 
2. Make changes to the code 
3. Rebuild and run the container 

```
docker-compose down
docker-compose build
docker-compose up
```

### Troubleshooting

Check logs with docker-compose logs or docker logs <container-id>
Ensure AWS credentials have the necessary permissions
Verify that the S3 bucket exists and is accessible

