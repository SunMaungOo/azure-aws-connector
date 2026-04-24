import boto3
from pathlib import Path
import logging
from fastapi import FastAPI,HTTPException
from model import DataStructure
from typing import Dict
from azure_datalake import AzureDataLake
from config import DATA_LAKE_SAS,DATA_FOLDER,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,HOST,PORT,TOKEN
import uvicorn

logging.basicConfig(
    level=logging.INFO,\
    format="%(asctime)s | %(levelname)-8s | %(name)-15s | %(lineno)-3d | %(message)s",\
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger("azure-aws-gateway")

app = FastAPI()

def upload_file(aws_access_key_id:str,\
                aws_secret_access_key:str,\
                local_file_path:str,\
                dest_file_path:str,\
                bucket_name:str)->bool:
    try:
        s3 = boto3.client("s3",\
                          aws_access_key_id=aws_access_key_id,\
                          aws_secret_access_key=aws_secret_access_key)
        
        s3.upload_file(local_file_path,\
                       bucket_name,\
                       dest_file_path)

        return True
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")

    return False

@app.post("/transfer/s3",status_code=200)
def transfer_to_s3(item:DataStructure)->Dict[str,str]:

    if TOKEN is None:
        raise HTTPException(status_code=500,\
                           detail="Server not configured with token")
    
    if item.token!=TOKEN:
       raise HTTPException(status_code=401,\
                           detail="Invalid token")

    data_path = Path(DATA_FOLDER)

    data_path.mkdir(parents=True,\
                    exist_ok=True)

    downloaded_file_name = ""

    with AzureDataLake(storage_account=item.azure_storage_account,\
                       credential=DATA_LAKE_SAS) as datalake:
        
        azure_file_name = item.azure_file_name

        if azure_file_name.startswith("/"):
            azure_file_name = azure_file_name[1:len(azure_file_name)]

        downloaded_file_name = f"{DATA_FOLDER}/{azure_file_name}"

        if not datalake.download_file(
            container_name=item.azure_container,\
            dir_path=item.azure_folder_path,\
            file_name=azure_file_name,\
            local_file_path=downloaded_file_name
        ):
            logger.error("Downloaded failed")

            raise HTTPException(
                status_code=500,\
                detail="Failed to download file from Azure Data Lake"
            )
        
    s3_folder_path = item.s3_folder_path

    if s3_folder_path.startswith("/"):
        s3_folder_path = s3_folder_path[1:len(s3_folder_path)]

    s3_dest_path = f"{s3_folder_path}/{item.s3_file_name}"

    if not upload_file(
        aws_access_key_id=AWS_ACCESS_KEY_ID,\
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,\
        local_file_path=downloaded_file_name,\
        dest_file_path=s3_dest_path,
        bucket_name=item.s3_bucket
    ):
        logger.error("Upload to S3 failed")

        raise HTTPException(status_code=500,\
                            detail="Failed to upload file to S3")
        
    downloaded_file_path = Path(downloaded_file_name)

    try:
        downloaded_file_path.unlink(missing_ok=True)
    except Exception as e:
        logger.warning(f"Failed to delete temp file: {e}")

    return {"message":"Upload successful",\
            "s3_path":s3_dest_path}

if __name__=="__main__":
    uvicorn.run(
        app=app,\
        host=HOST,\
        port=PORT
    )

