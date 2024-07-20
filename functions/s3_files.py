import boto3
import logging

s3 = boto3.client('s3')
logger = logging.getLogger()

def get_files(bucket_name,key_name,filepath):
    response = s3.download_file(bucket_name,key_name,filepath)
    if response == None:
        response = "File downloaded!"
        logger.info(response)
    return response