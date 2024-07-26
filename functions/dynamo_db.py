# May need to add function for updating message_id
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

def query_data(object):
    min_time = str(object[object['min_time']])
    max_time = str(object[object['max_time']])

    try:
        condition = f'timestamp > :{min_time} AND timestamp < :{max_time}'
        response = db.query(TableName=tableName,KeyConditionExpression=condition)
        items = response.get('Items',None)
        return items
    except Exception as e:
        message = "ERROR: {}".format(e)
    return message

