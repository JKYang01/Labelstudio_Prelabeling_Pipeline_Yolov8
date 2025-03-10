# save different formats of output for different annotation tools
import os
from pipeline_utils.utils import DEFAULT_CFG
class Formats:
    def __init__(self,**kwargs):
        self.i = kwargs.get('i')
        self.x1 = kwargs.get('x1')
        self.x2 = kwargs.get('x2')
        self.y1 = kwargs.get('y1')
        self.y2 = kwargs.get('y2')
        self.box_cls = kwargs.get('box_cls',None)
        self.box_conf = kwargs.get('box_conf')
        self.label = kwargs.get('label')
        self.original_width = kwargs.get('original_width')
        self.original_height = kwargs.get('original_height')
        self.scale = kwargs.get('scale',1)  # Example of a default value
        self.format = kwargs.get('format',None)
        self.image_name = os.path.basename(kwargs.get('image_url'))
        # self.bucket_name = kwargs.get('bucket_name',DEFAULT_CFG.get('bucket_name'))

    def label_studio_pred(self):
        # if format=='label_studio':
        ''' label studio format for each prediction:
        {
                "from_name" : self.from_name,
                "to_name" : self.to_name,
                "id": str(i),
                "type": "rectanglelabels",
                "score": box_conf.item(),
                "original_width": original_width,
                "original_height": original_height,
                "image_rotation": 0,
                "value": {
                    "x":x,
                    "y":y,
                    "width":width,
                    "height":height,
                    "rectanglelabels": [self.labels[int(box_cls.item())]]
                }
        }
        '''
        x= self.x1 / (self.scale*self.original_width) * 100.0
        y= self.y1 / (self.scale*self.original_height) * 100.0
        width=(self.x2-self.x1)/ (self.scale*self.original_width) * 100.0
        height=(self.y2-self.y1)/ (self.scale*self.original_height) *100.0

        return {
            "id": str(self.i),
            "type": "rectanglelabels",        
            "from_name": "label", 
            "to_name": "image",
            "score":self.box_conf,
            "original_width": self.original_width, 
            "original_height": self.original_height,
            "image_rotation": 0,
            "value": {
                    "rotation": 0,          
                    "x": x, 
                    "y": y,
                    "width": width, 
                    "height": height,
                    "rectanglelabels":[self.label]
                    }
                }
        
    @staticmethod
    def label_studio_final(image_url: str, model_version: str, predictions: list, bucket_name=None):
        # if bucket_name is None:
        #     bucket_name = DEFAULT_CFG.get('bucket_name')
        return {
                "data":{"image":f"{image_url}"},
                "predictions":[{
                "model_version": model_version,
                "result":predictions  
                    }]
                }
    
    def diffgram_format(self):
        # i = kwargs.get('i')
        x1 = self.x1
        x2 = self.x2
        y1 = self.y1
        y2 = self.y2
       # Example of a default value

        xmin= (x1 / self.scale)
        ymin= (y1 / self.scale)
        xmax= (x2 / self.scale)
        ymax= (y2 / self.scale)

        data = {"file_name": self.image_name,
                "name":self.label,
                "number":self.box_cls,
                "type":"box",
                "x_min":xmin,
                "x_max":xmax,
                "y_min":ymin,
                "y_max":ymax,
                "score": self.box_conf
                }
        return data 
