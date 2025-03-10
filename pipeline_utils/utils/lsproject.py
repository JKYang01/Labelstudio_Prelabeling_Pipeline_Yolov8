# from label_studio_sdk.label_interface import LabelInterface
from label_studio_sdk import Webhook
from label_studio_sdk.client import LabelStudio
from pipeline_utils.utils.ls_cfg import LS_CFG,CONFIG_FOLDER
import json
import logging 
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class LS_Project:
    def __init__(self):
        # self.config = cfg.load_config("labelstudio_config.yaml")
        self.config=LS_CFG
        self.ls = LabelStudio(
        base_url="https://app.humansignal.com",
        api_key=self.config.API_KEY,
        )
    def get_project_id(self, project_name: str) -> object:
        response = self.ls.projects.list()
        for item in response:
            if item.title == project_name:
                return item.id

    def create_new_project(self,import_bucket:str=None,folder:str=None,project_name:str=None,project_type:str=None):
        
        if import_bucket is None:
            import_bucket=self.config.import_bucket_name

        if folder is None:
            folder = self.config.prefix

        if project_type=="rectanglelabels":
            with open(CONFIG_FOLDER/self.config.bbx_label_config_xml,'r')as f:
                label_config_string = f.read()
            
            project = self.ls.projects.create(
            title=project_name,
            description="annotate",
            show_skip_button=True,
            maximum_annotations=2,
            label_config=label_config_string,
            show_collab_predictions=True
            )
            
            project_id = project.id
        
            self.ls.import_storage.s3.create(
                    regex_filter = ".*json",
                    presign=False,
                    recursive_scan=False,
                    project = project_id,
                    description="bbx labeling",
                    bucket = import_bucket,
                    prefix = folder,
                    aws_access_key_id=self.config.aws_access_key_id,
                    aws_secret_access_key=self.config.aws_secret_access_key,
                    region_name=self.config.region_name,
                    use_blob_urls=False,

                )
            
            storage_id = self.ls.import_storage.s3.list(project=project_id)[0].id
            self.ls.import_storage.s3.sync(
            id=storage_id )
            

        if project_type=="captioning":
            with open(CONFIG_FOLDER/self.config.caption_tag_xml,'r')as f:
                label_config_string = f.read()

            project = self.ls.projects.create(
                title=project_name,
                description="tag numbers",
                show_skip_button=True,
                maximum_annotations=1,
                label_config=label_config_string,
                show_collab_predictions=False
            )
        
            project_id = project.id
        
            self.ls.import_storage.s3.create(
                    regex_filter = ".*(png|jpe?g|tiff)",
                    presign=False,
                    recursive_scan=False,
                    project = project_id,
                    description="tag",
                    bucket = import_bucket,
                    prefix = folder,
                    aws_access_key_id=self.config.aws_access_key_id,
                    aws_secret_access_key=self.config.aws_secret_access_key,
                    region_name=self.config.region_name,
                    use_blob_urls=False,

                )
            storage_id = self.ls.import_storage.s3.list(project=project_id)[0].id
            self.ls.import_storage.s3.sync(
            id=storage_id )
        
        # self.ls.export_storage.s3.create(
        #     project = project_id,
        #     description="humanlabel",
        #     bucket = self.config.export_bucket_name,
        #     prefix = f"{self.config.prefix.split('/')[0]}/{project_id}/prod/output",
        #     aws_access_key_id=self.config.aws_access_key_id,
        #     aws_secret_access_key=self.config.aws_secret_access_key,
        #     region_name=self.config.region_name
        #     )

        # if self.config.WEBHOOK:
        #     self.ls.webhooks.create(
        #         url=self.config.WEBHOOK,
        #         project=project_id,
        #         is_active=True,
        #         send_for_all_actions=False,
        #         actions=["ANNOTATION_CREATED"]
        #         )
        
        status = {project_id:{
                "title":project_name,
                "status":"created"}}
        logger.info(status)
        print(status)
        

    def change_import_data(self,project_id,import_bucket,folder):
        storage_id = self.ls.import_storage.s3.list(project=project_id)[0].id
        self.ls.import_storage.update(id=storage_id,
                regex_filter = ".*json",
                presign=False,
                recursive_scan=False,
                project = project_id,
                description="prelabel",
                bucket = import_bucket,
                prefix = folder,
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key,
                region_name=self.config.region_name,
                use_blob_urls=False
                )
        self.ls.import_storage.s3.sync(id=storage_id)

        



        
    