from pathlib import Path
from pipeline_utils.utils import extract_filename_without_suffix
from pdf_piece.base_detection.detect_base import base_detect
from pipeline_utils.utils import DEFAULT_CFG,CLASSES,DEVICE,get_cfg
from pipeline_utils.utils.formats import Formats
from pipeline_utils.utils.s3_load import img_from_s3, upload_json_to_s3
from PIL import Image
from pdf_piece.partial_detection.pic_tile import MediumTile
from pipeline_utils.utils.log import setup_logger

logger = setup_logger(__name__)

class FullpicDetect:

    def __init__(self,confg=DEFAULT_CFG,overrides=None):
        self.overrides = overrides
        self.args= get_cfg(confg, overrides)
        self.model_path=f"{self.args.temp_dir}/model.pt"
        self.input_path = self.args.input_path
        self.output_path = self.args.temp_dir
        self.classes=CLASSES
        self.class_ids=self.args.class_ids
        self.filter_thresh=self.args.thresholds
        self.model_version=self.args.model_version
        self.tile_size=self.args.tile_size
        self.scale=self.args.scale
        self.temp_dir=self.args.temp_dir
        if DEVICE=='cpu':
            self.device='cpu'
        else:
            self.device=self.args.device
        self.format=self.args.format
        self.save_piece=self.args.save_piece

        print("if save the piece or not ", self.save_piece)


    def detect_image(self,input_image_path,from_s3=True):
        # input_image_path=re.sub(r"\.pdf$",".png",input_pdf_path)
        image_name = extract_filename_without_suffix(input_image_path)
        model_path=self.model_path
        labels=self.classes
        class_ids=self.class_ids
        
        # start detecting
        if from_s3:
            image = img_from_s3(input_image_path)
        else:
            image = Image.open(input_image_path)
        image_width, image_height=image.size
        params = {
                    'image':None, # the original image
                    'input_path':self.input_path,
                    'bucket_name':self.args.bucket_name,
                    'temp_dir':self.temp_dir,
                    'model_path':model_path,
                    'original_width':image_width,
                    'original_height':image_height,
                    'image_url':input_image_path,
                    'output_path':self.output_path,
                    'model_version':self.model_version,
                    'labels':labels,
                    'class_ids':class_ids,
                    'scale':self.scale,
                    'filter_thresh':self.filter_thresh,
                    'device':self.device,
                    'format':self.format,
                    'save_piece':self.save_piece,
                    'detection_task':self.args.task_name
                }
        # if self.save_piece: # crop into small piece exclude drawing, horizontal and vertical area
        #     params['class_ids']=self.args.p_class_ids
        #     self.cropping_predict(params,input_image_path)
        # else:
        predictions, format_predictions = base_detect(**params)
        final_prediction = Formats.label_studio_final(image_url= input_image_path,
                                                      model_version=self.args.model_version,
                                                      predictions=format_predictions,
                                                      bucket_name=self.args.bucket_name)
        upload_json_to_s3(
            f'{self.input_path}ml_predictions/ann/{self.args.task_name}/tasks_{image_name}.json',
            final_prediction, bucket=self.args.bucket_name)


    def cropping_predict(self,params,input_image_path):
        try:
            drawing_tire = MediumTile(overrides=self.overrides, **params)
            l_predictions, f_predictions, final_predictions = drawing_tire.create_task_ppl(input_image_path=input_image_path)
            return l_predictions, f_predictions, final_predictions
        except MemoryError as e:
            logger.error(
                f"MemoryError encountered {e}. Consider reducing the size of tasks or the number of processes.",
                exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise

            
