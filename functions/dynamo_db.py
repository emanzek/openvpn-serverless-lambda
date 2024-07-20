import boto3
import logging

db = boto3.client('dynamodb')
logger = logging.getLogger()
tableName = 'openvpn-auth'


def put_data(object):
    try:
        db.put_item(TableName=tableName,Item=object)
        message = ("Data added!")
    except Exception as e:
        message = "ERROR: {}".format(e)
    logger.info(message)

def get_data(object):
    try:
        response = db.get_item(TableName=tableName,Item=object)
        item = response.get('Item',None)
        return item
    except Exception as e:
        message = "ERROR: {}".format(e)
    return message

