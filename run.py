from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pipeline_utils.utils import DEFAULT_CFG,get_cfg
from pipeline_utils.utils.ls_cfg import LS_CONFIG_DIR
from pipeline_utils.utils.lsproject import LS_Project
from pipeline_utils.utils.s3_load import check_link,get_png_files_from_s3,download_model
from pathlib import Path
from pdf_piece.base_detection.detect import FullpicDetect
import yaml
from pipeline_utils.utils.log import setup_logger
logger = setup_logger(__name__)
import torch
logger.info(torch.__version__)  # PyTorch version
logger.info(torch.cuda.is_available())  # Should return True if PyTorch detects your GPU
logger.info(torch.version.cuda)  # CUDA version PyTorch is built with
logger.info(torch.backends.cudnn.enabled)


class PDFProcessor:
    def __init__(self,**kwargs):
        if '__file__' in globals():
            # If running as a script
            self.script_dir = Path(__file__).resolve().parent
        else:
            # If running in a Jupyter Notebook
            self.script_dir = Path(os.getcwd()).resolve()
        self.setup_overrides(**kwargs)
        self.params = get_cfg(DEFAULT_CFG,self.overrides)
        Path(f"{self.params.temp_dir}").mkdir(parents=True, exist_ok=True)

        with open(LS_CONFIG_DIR, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)

        data.update(credential)

        with open(LS_CONFIG_DIR, 'w') as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False)

        local_path = f"{self.params.temp_dir}/model.pt"
        download_model(model_path=self.params.s3_model_path, local_path=local_path)

    def setup_overrides(self,**kwargs):
        # bucket,directory = check_link(self.project_data.sheet_saved_at)
        bucket = kwargs.get('bucket_name')
        directory = kwargs.get('input_path')
        # parent_dir = Path(directory).parent # parent directory of where the sheet got saved
        self.overrides = {
            "bucket_name": bucket,
            "input_path": directory,
            "output_path": f"{self.script_dir}/temp/work",
            "temp_dir": f"{self.script_dir}/temp",
            **kwargs,
        }

    def pre_annotate_pngs(self):
        png_path_list = get_png_files_from_s3(self.params.bucket_name,self.params.input_path)
        fullpic = FullpicDetect(overrides=self.overrides)
        for input_png_path in png_path_list:
            print(input_png_path)
            fullpic.detect_image(input_png_path)



    def create_annotation_project(self,project_title):
        # with open(LS_CONFIG_DIR, 'w') as yaml_file:
        #     yaml.dump(data, yaml_file, default_flow_style=False)

        LS_Project().create_new_project(project_name=project_title,
                                        project_type="rectanglelabels",
                                        folder=f"{self.params.input_path}ml_predictions/ann/{self.params.task_name}")






if __name__ == "__main__":
    import os
    from datetime import datetime, timezone

    # Get values from environment variables with defaults
    overrides = {
        "save_piece": os.environ.get("SAVE_PIECE", "False").lower() == "false",
        "tile_size": int(os.environ.get("TILE_SIZE", 640)),
        "bucket_name": os.environ.get("BUCKET_NAME", ""),
        "input_path": os.environ.get("INPUT_PATH", ""),
        "output_path": os.environ.get("OUTPUT_PATH", ""),
        "task_name": os.environ.get("TASK_NAME", ""),
    }

    input_path = os.environ.get("INPUT_PATH", "")
    task_name = os.environ.get("TASK_NAME", "")

    credential = {
        "import_bucket_name": os.environ.get("IMPORT_BUCKET_NAME", ""),
        "prefix": f"{input_path}ml_predictions/ann/{task_name}",
        "URL": os.environ.get("URL", "https://app.humansignal.com/api/projects/"),
        "API_KEY": os.environ.get("API_KEY", ""),
        "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", ""),
        "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        "region_name": os.environ.get("AWS_REGION", "")
    }


    pdf_processor = PDFProcessor(**overrides)
    pdf_processor.pre_annotate_pngs()
    pdf_processor.create_annotation_project(project_title=f"{input_path}_{task_name}")






