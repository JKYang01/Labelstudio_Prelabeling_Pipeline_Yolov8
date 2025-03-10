# tire the pdf into medium size for running door/window/.. medium size symbols  and text object detection 

from PIL import Image
from pdf_piece.base_detection.detect_base import medium_detect
from pipeline_utils.utils import DEFAULT_CFG, CLASSES, DEVICE, ppl, get_cfg, extract_filename_without_suffix
import torch
from pipeline_utils.utils.s3_load import upload_file_to_s3, upload_json_to_s3, img_from_s3, upload_img_to_s3
from pipeline_utils.utils.formats import Formats
from concurrent.futures import ProcessPoolExecutor, as_completed
from threading import Lock
from pipeline_utils.utils.log import setup_logger

logger = setup_logger(__name__)
gpu_lock = Lock()


class MediumTile:
    ''' tire the big image into medium size pictures, default size is 5000X5000
        Attributes: 
        model_path
        input_path: the input path for imput images
        output_path: the output path for the json files and tired pictures 
        tile_size: default is 1000
        model_version: default is "v8x_oct19"
        scale: default is 1.0
    '''

    def __init__(self, config=DEFAULT_CFG, overrides=None, classes=CLASSES, **kwargs):
        self.args = get_cfg(config, overrides)
        self.model_path = kwargs.get("model_path")
        self.input_path = self.args.input_path
        self.output_path = kwargs.get("output_path")
        self.classes = classes
        self.class_ids = kwargs.get("class_ids")  # object class for medium size tire
        self.filter_thresh = kwargs.get("thresholds", self.args.thresholds)
        self.model_version = kwargs.get("model_version")
        self.tile_size = self.args.tile_size
        self.scale = self.args.scale
        if DEVICE == 'cpu':
            self.device = 'cpu'
        else:
            self.device = DEVICE
        self.format = self.args.format
        self.save_piece = self.args.save_piece
        self.original_width = kwargs.get("original_width")
        self.original_height = kwargs.get("original_height")
        self.image_url = kwargs.get("image_url")
        self.initial_id = kwargs.get("id", 0)
        self.task_name = kwargs.get("detection_task")

    def generate_tasks(self, input_image_path):
        img_name = extract_filename_without_suffix(input_image_path)
        tasks = []
        # with Image.open(input_image_path) as img:
        #     img.load()
        img = img_from_s3(input_image_path)
        w, h = img.size
        # tasks = [(input_image_path,x, y) for x in range(0,w, int(self.tile_size/2)) for y in range(0, h, int(self.tile_size/2))]
        i = 0
        while i + self.tile_size <= w:
            t_w = self.tile_size
            j = 0
            while j + self.tile_size <= h:
                t_h = self.tile_size
                self.process_img(img, img_name, i, j, t_w, t_h)
                tasks.append((img_name, i, j))
                j += int(self.tile_size / 2)
            # get vertical edge
            if j < h:
                t_h = int(h - j)
                self.process_img(img, img_name, i, j, t_w, t_h)
                tasks.append((img_name, i, j))

            i += int(self.tile_size / 2)

        # get horizontal edge
        if i < w:
            t_w = int(w - i)
            j = 0
            while j + self.tile_size <= h:
                t_h = self.tile_size
                self.process_img(img, img_name, i, j, t_w, t_h)
                tasks.append((img_name, i, j))
                j += int(self.tile_size / 2)

            # Handle the bottom-right corner
            if j < h:
                t_h = int(h - j)
                self.process_img(img, img_name, i, j, t_w, t_h)
                tasks.append((img_name, i, j))
            # for x in range(0,w, int(self.tile_size/2)):
            #     for y in range(0, h, int(self.tile_size/2)):
            #         self.process_img(img,img_name,x,y,t_w,t_h)
            #         tasks.append((img_name,x, y))
        return tasks

    def process_img(self, img, img_name, x, y, t_w, t_h):
        box = (x, y, x + t_w, y + t_h)
        cropped_image = img.crop(box)
        # self.w,self.h = cropped_image.size
        # Path(f"{self.output_path}/{img_name}").mkdir(parents=True, exist_ok=True)
        cropped_img_path = f"{self.output_path}/{img_name}_{x}_{y}.png"
        cropped_image.save(cropped_img_path)
        tile_pic_path = f'{self.input_path}ml_predictions/ann/{self.task_name}/{img_name}_{x}_{y}.png'
        if self.save_piece:
            upload_file_to_s3(f"{cropped_img_path}", tile_pic_path, bucket=self.args.bucket_name)

    def detect_image(self, img_name, x, y, device: str = '0'):
        # with Image.open(input_image_path) as drawing_img:
        try:
            cropped_img_path = f"{self.output_path}/{img_name}_{x}_{y}.png"
            cropped_name = f'{img_name}_{x}_{y}'
            tile_pic_path = f'{self.input_path}ml_predictions/ann/{self.task_name}/{cropped_name}.png'

            if DEVICE == 'cpu':
                sub_device = 'cpu'
            elif len(self.device) > 1:
                sub_device = device
            else:
                sub_device = self.device
            # with Image.open(tile_pic_path) as image:
            # image_width, image_height=image.size
            params = {  # cropped image
                'id': self.initial_id,
                'x': x,
                'y': y,
                'model_path': self.model_path,
                'original_width': self.original_width,
                'original_height': self.original_height,
                'image_url': self.image_url,
                'detect_image_url': cropped_img_path,
                'cropped_name': cropped_name,
                'output_path': self.output_path,
                'model_version': self.model_version,
                'labels': self.classes,
                'class_ids': self.class_ids,
                'scale': self.scale,
                'filter_thresh': self.filter_thresh,
                'device': sub_device,
                'format': self.format,
                "save_piece": self.save_piece
            }
            predictions, format_predictions = medium_detect(**params)
            final_prediction = {}
            if sub_device != 'cpu':
                with gpu_lock:
                    torch.cuda.synchronize()
            if self.format == 'label_studio':
                final_prediction = Formats.label_studio_final(image_url=tile_pic_path,
                                                              model_version=self.args.model_version,
                                                              predictions=format_predictions,
                                                              bucket_name=self.args.bucket_name)
                upload_json_to_s3(
                    f'{self.input_path}ml_predictions/ann/{self.task_name}/{img_name}/tasks_{cropped_name}.json',
                    final_prediction, bucket=self.args.bucket_name)
        except Exception as e:
            logger.error(f"Error in detect_image at position ({x}, {y}) with device {device}: {e}", exc_info=True)
            return None, None, None
        return predictions, format_predictions, final_prediction

    def create_task_ppl(self, input_image_path):
        # parallel processing pictures
        ## dev make option of import s3 bucket (?)
        tasks = self.generate_tasks(input_image_path)
        f_predictions = []
        l_predictions = []
        final_predictions = []
        if ppl == True and DEVICE != 'cpu' and len(DEVICE) > 1:
            chunk_size = len(DEVICE)
            tasks_ppl = [(param[0], param[1], param[2], f'cuda:{index % len(DEVICE)}') for index, param in
                         enumerate(tasks)]
            with ProcessPoolExecutor(max_workers=chunk_size) as executor:
                future_to_task = {
                    executor.submit(self.detect_image, input_image_path, x, y, n): (x, y)
                    for input_image_path, x, y, n in tasks_ppl
                }

                for future in as_completed(future_to_task):
                    try:
                        predictions, format_predictions = future.result()
                        l_predictions.extend(predictions)
                        f_predictions.extend(format_predictions)
                    except Exception as e:
                        logger.error(
                            f"Error processing task at {input_image_path} position ({future[1]}, {future[2]}): {e}")
                    finally:
                        torch.cuda.empty_cache()

        else:
            for task in tasks:
                predictions, format_predictions, final_prediction = self.detect_image(task[0], task[1], task[2])
                if predictions or format_predictions:
                    l_predictions.extend(predictions)
                    if self.format:
                        f_predictions.extend(format_predictions)
                        final_predictions.append(final_prediction)

                if DEVICE != 'cpu':
                    torch.cuda.empty_cache()

        return l_predictions, f_predictions, final_predictions


if __name__ == '__main__':
    # Create an instance of medium_tire
    tire = MediumTile()
    # Call create_slice_ppl with the defined parameters
    input_image_path = input("Please enter the input image path: ")
    tire.create_task_ppl(input_image_path)
