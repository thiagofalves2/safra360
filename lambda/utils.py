import logging
import os
import boto3
import requests
from requests import Request, Session
from botocore.exceptions import ClientError
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def create_presigned_url(object_name):
    """Generate a presigned URL to share an S3 object with a capped expiration of 60 seconds

    :param object_name: string
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3',
                             region_name=os.environ.get('S3_PERSISTENCE_REGION'),
                             config=boto3.session.Config(signature_version='s3v4',s3={'addressing_style': 'path'}))
    try:
        bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=60*1)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

""" Function to call API token. """
def get_token():
    token_host = "https://idcs-902a944ff6854c5fbe94750e48d66be5.identity.oraclecloud.com"
    token_key = "OThiMmEwZDY0MWQ0NDFmZDhmMWQyOTdlNDg3NjFmMzk6ZDczMjU5YWYtYzJhZC00MTMzLWI0NjEtNDYyN2IwN2VlMDZj"
    token_body = "grant_type=client_credentials&scope=urn:opc:resource:consumer::all"
    token_url = '{}/oauth2/v1/token'.format(token_host)
    token_headers = {'Authorization': 'Basic ' + token_key, 'Content-Type': 'application/x-www-form-urlencoded'}
    
    logger.info("Token url: {}".format(token_url))
    logger.info("Token headers: {}".format(token_headers))
    
    try:
        request_token = requests.post(token_url, headers=token_headers, data=token_body)
        response_token = request_token.json()
        response_token_status = request_token.status_code
        logger.info("Token API status code: {}".format(response_token_status))
        token = response_token['access_token']
    except Exception as e:
        logger.error("There was a problem connecting to the Token API: {}".format(e))
        return ''
        
    logger.info("Token API result: {}".format(token))
    
    return token

""" Function to call Safra API. """
def call_safra_api(option, account_number):
    safra_host = "https://af3tqle6wgdocsdirzlfrq7w5m.apigateway.sa-saopaulo-1.oci.customer-oci.com/fiap-sandbox"
    safra_url = '{safra_host}/open-banking/v1/accounts/{account_number}{option}'.format(safra_host=safra_host,account_number=account_number,option=option)
    
    token = get_token()
    
    if (token == '') :
        logger.error("Empty token.")
        return ''
    else :
        safra_headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    
    #session = Session()
    #prepped = Request('GET', safra_url, headers=safra_headers).prepare()
    #r_safra = session.send(prepped)
    #r_safra_status_code = r_safra.status_code
    
    try:
        request_safra = requests.get(safra_url, headers=safra_headers)
        response_safra = request_safra.json()
        response_safra_status = request_safra.status_code
        logger.info("Safra API status code: {}".format(response_safra_status))
        logger.info("Safra API result: {}".format(str(response_safra)))
    except Exception:
        logger.error("There was a problem connecting to the Safra API.")
        return ''
        
    return response_safra

""" Function to call SMS API. """
def sms_controller(cpf):
    base_url = "http://3.133.16.98:8085"
    endpoint = '{base_url}/sms/{cpf}'.format(base_url=base_url,cpf=cpf)
    
    logger.info('Final endpoint: {}'.format(endpoint))
    
    try:
        request_sms = requests.post(endpoint)
        response_sms = request_sms.json()
        response_sms_status = request_sms.status_code
        logger.info("SMS API status code: {}".format(response_sms_status))
        logger.info("SMS API result: {}".format(str(response_sms)))
        
        return response_sms_status
    except Exception as e:
        logger.error("There was a problem connecting to the SMS API: {}".format(e))
        return ''

""" Function to call validate SMS token API. """
def token_controller(cpf, token):
    base_url = "http://3.133.16.98:8085"
    endpoint = '{base_url}/token/{cpf}/{token}'.format(base_url=base_url,cpf=cpf,token=token)
    
    try:
        request_token_validation = requests.post(endpoint)
        response_token_validation = request_token_validation.json()
        response_token_validation_status = response_token_validation['httpStatus']
        logger.info("Token Validation API status code: {}".format(response_token_validation_status))
        logger.info("Token Validation API result: {}".format(str(response_token_validation)))
        
        return response_token_validation_status
    except Exception as e:
        logger.error("There was a problem connecting to the Token Validation API: {}".format(e))
        return ''
    
    """ Function to call authentication controller services. """
def authentication_controller(option, cpf, date):
    base_url = "http://3.133.16.98:8085"
    endpoint = '{base_url}/{option}/{cpf}/{date}'.format(base_url=base_url,option=option,cpf=cpf,date=date)
    
    logger.info('Final endpoint: {}'.format(endpoint))
    
    try:
        request = requests.post(endpoint)
        response = request.json()
        response_status = request.status_code
        logger.info("Token Validation API status code: {}".format(response_status))
        logger.info("Token Validation API result: {}".format(str(response)))
        
        return response
    except Exception as e:
        logger.error("There was a problem connecting to the Authentication Controller API: {}".format(e))
        return ''

