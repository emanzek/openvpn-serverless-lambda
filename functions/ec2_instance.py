import os
import boto3
import logging

logger = logging.getLogger()
cf = boto3.client('cloudformation')

def create():
  logger.info("Creation Executed")
  try:
    response = cf.create_stack(
      StackName="OpenVPN-EC2",
      TemplateURL=os.environ.get('CF_TEMPLATE_URL'),
      Capabilities=['CAPABILITY_IAM']
    )
    logger.info("Cloudformation response: %s", response)
  except Exception as e:
    logger.info("Cloudformation response: %s", e)

  return "This process will take for a while to complete, we will provide you a configuration file soon..."


def destroy():
    try:
      cf.delete_stack(StackName="OpenVPN-EC2")
      logger.info("Deletion Executed")
    except Exception as e:
      logger.error("Found an error with message: %s",e)
    return "Deleting VPN resources..."