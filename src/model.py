from pydantic import BaseModel

class DataStructure(BaseModel):
    azure_storage_account:str
    azure_container:str
    azure_folder_path:str
    azure_file_name:str
    s3_bucket:str
    s3_folder_path:str
    s3_file_name:str