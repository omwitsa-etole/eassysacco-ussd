import datetime
import json
import requests
import base64
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA256
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.x509 import load_pem_x509_certificate

import os

CONSUMER_KEY: str = ""
CONSUMER_SECRET: str = ""
PASSKEY: str = ""
SHORT_CODE: str = ""
ACCOUNT_TYPE: str = ""
APP_USERNAME:str = ""
PASSWORD:str = ""
CERT = 'ProductionCertificate.cer'
def _get_trans_type():
    if ACCOUNT_TYPE == "PAYBILL":
        trans_type = "CustomerPayBillOnline"
    else:
        trans_type = "CustomerBuyGoodsOnline"
    return trans_type

def generate_id():
    id = "feb5e3f2-fbbc-4745-844c-ee37b546f627"
    return id
    
def base64_encode(data):
    return base64.b64encode(data)
    
def encrypt_data(data, key, iv):
    # Padding data to ensure it's a multiple of the block size
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()

    # Encrypting data
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return encrypted_data
    
def getCert():
    return padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None)

def generate_signed_token(private_key_path,password):
    #"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    with open(private_key_path, 'r') as key_file:
        public_key = key_file.read()

    #cipher_rsa = PKCS1_v1_5.new(public_key)
    #encrypted_password = cipher_rsa.encrypt(password.encode('utf-8'))
    #security_credential = base64.b64encode(encrypted_password).decode('utf-8')
    certificate = load_pem_x509_certificate(public_key.encode(), backend=default_backend())
    public_key = certificate.public_key()
    concatenated =f"{SHORT_CODE}{PASSWORD}"
    encrypted = public_key.encrypt(
        concatenated.encode('utf-8'),
        padding.PKCS1v15()
    )
    security_credential = base64.b64encode(encrypted)#.decode('utf-8')
    #print("credential",security_credential)
    """
    with open(private_key_path, 'r') as key_file:
        certificate = key_file.read()
    key = os.urandom(32)  # 256-bit key
    iv = os.urandom(16)  # 128-bit IV
    combined_data = f"{PASSWORD}{certificate}".encode()
    # Encrypt combined data
    encrypted_data = encrypt_data(combined_data, key, iv)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # Base64 encode the encrypted data
    encoded_data = base64_encode(encrypted_data)
    """
    return [ security_credential.decode('utf-8'),timestamp]

def _get_password():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = SHORT_CODE + PASSKEY + timestamp

    online_password = base64.b64encode(data_to_encode.encode('ascii'))
    decode_password = online_password.decode('utf-8')
    return [decode_password,timestamp]

def get_token() -> dict:
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    encoded_creds = f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()
    b64_creds = base64.b64encode(encoded_creds)
    ic = "cFJZcjZ6anEwaThMMXp6d1FETUxwWkIzeVBDa2hNc2M6UmYyMkJmWm9nMHFRR2xWOQ==";
    #ic = b64_creds.decode()
    #b64_creds.decode('utf-8')
    payload = {}
    print("basic ",ic)
    headers = {
        'Authorization': f"Basic {ic}"
    }
    #sprint(encoded_creds)
    response = requests.request("GET", url, headers=headers)
    if response.status_code >= 200 and response.status_code < 300:
        
        try:
            print("access_token=>",dict(response.json()))
            return dict(response.json())
        except Exception as e:
            pass
    return {'access_token':None,'expires_in':3600}

async def trigger_stk_push(phone_number: int, amount: int, callback_url: str, account_ref: str, description: str,token) -> dict:
    #print("access_token=>",token)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    pwd = _get_password()
    payload = {
        "BusinessShortCode": ""+str(int(SHORT_CODE)),
        "Password": pwd[0],
        "Timestamp": ""+str(pwd[1]),
        "TransactionType": _get_trans_type(),
        "Amount": amount,
        "PartyA": ""+str(phone_number),
        "PartyB": ""+str(SHORT_CODE),
        "PhoneNumber": ""+str(phone_number),
        "CallBackURL": callback_url,
        "AccountReference": account_ref,
        "TransactionDesc": description
    }
    #print(payload)
    response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
                                headers=headers, data=json.dumps(payload))
    if response.status_code >= 200 and response.status_code < 300:
        try:
            return dict(response.json())
        except Exception as e:
            pass
    return dict({'message': response.json()['errorMessage'] if response.json().get('errorMessage') else 'Failed to initiate request with code '+str(response.status_code)})
async def query_stk_push(checkout_request_id: str,token) -> dict:

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    pwd = _get_password()
    payload = {
        "BusinessShortCode": int(SHORT_CODE),
        "Password": pwd[0],
        "Timestamp": ""+str(pwd[1]),
        "CheckoutRequestID": checkout_request_id,
    }
    print(json.dumps(payload))
    response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query', headers=headers,
                                data=json.dumps(payload))
    if response.status_code >= 200 and response.status_code < 300:
        try:
            return dict(response.json())
        except:
            pass
    print(response.json())
    return dict({'message': response.json()['errorMessage'] if response.json().get('errorMessage') else 'Failed to initiate request with code '+str(response.status_code)})

async def query_balance(result_url,token) -> dict:

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    pwd = generate_signed_token(CERT,PASSWORD)
    payload = {
        "SecurityCredential": pwd[0],
        "Initiator": APP_USERNAME,
        "Remarks": "account-balance",
        "QueueTimeOutURL": result_url,
        "ResultURL": result_url,
        #"BusinessShortCode": int(SHORT_CODE),
        #"Password": pwd[0],
        "Timestamp": ""+str(pwd[1]),
        "CommandID": "AccountBalance",
        "IdentifierType": "4",
        "PartyA": int(SHORT_CODE),
    }
   
    response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/accountbalance/v1/query', headers=headers,
                                data=json.dumps(payload))
    if response.status_code >= 200 and response.status_code < 300:
        try:
            return dict(response.json())
        except:
            pass
    print(response.json())
    return dict({'message': response.json()['errorMessage'] if response.json().get('errorMessage') else 'Failed to initiate request with code '+str(response.status_code)})


async def query_transaction(transaction_id,result_url,token)->dict:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    pwd = generate_signed_token(CERT,PASSKEY)
    payload = {
        "BusinessShortCode": int(SHORT_CODE),
        "Initiator":APP_USERNAME,
        "Password": pwd[0],
        "SecurityCredential":pwd[0],
        "Timestamp": ""+str(pwd[1]),
        "TransactionID": transaction_id,
        "CommandID": "TransactionStatusQuery",
        "PartyA":int(SHORT_CODE),
        "ResultURL":result_url,
        "IdentifierType":"4",
        "QueueTimeOutURL":result_url,
        "Remarks":transaction_id,
        "Occasion":"OK",
    }
    print(json.dumps(payload))
    response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/transactionstatus/v1/query', headers=headers,
                                data=json.dumps(payload))
    if response.status_code >= 200 and response.status_code < 300:
        try:
            return dict(response.json())
        except:
            pass
    print(response.json())
    return dict({'message': response.json()['errorMessage'] if response.json().get('errorMessage') else 'Failed to initiate request with code '+str(response.status_code)})

async def business_to_customer(data,token) -> dict:
    #print("access_token=>",token)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    pwd = generate_signed_token(CERT,PASSWORD)
    
    #pwd = _get_password()
    payload = {
        #"OriginatorConversationID": generate_id(),
        "BusinessShortCode": ""+str(int(SHORT_CODE)),
        #"Password": PASSKEY,
        "Timestamp": ""+str(pwd[1]),
        "InitiatorName": APP_USERNAME,
        "SecurityCredential": pwd[0],
        "CommandID": "BusinessPayment",
        "Amount": data["amount"],
        "PartyA": int(SHORT_CODE),
        "PartyB": data["phone"],
        "Remarks": data['remarks'],
        "QueueTimeOutURL": data["result_url"],
        "ResultURL": data["result_url"],
        "Occasion": data["occassion"]
    }
    #print(json.dumps(payload))
    response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest',
                                headers=headers, data=json.dumps(payload))
    if response.status_code >= 200 and response.status_code < 300:
        try:
            return dict(response.json())
        except Exception as e:
            pass
    return dict({'message': response.json()['errorMessage'] if response.json().get('errorMessage') else 'Failed to initiate request with code '+str(response.status_code)})

async def business_to_business(data,token) -> dict:
    #print("access_token=>",token)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    #pwd = generate_signed_token(CERT,PASWORD)
    pwd = _get_password()
    payload = {
        "RequestRefID": generate_id(),
        "BusinessShortCode": ""+str(int(SHORT_CODE)),
        "Password": pwd[0],
        "Timestamp": ""+str(pwd[1]),
        "InitiatorName": APP_USERNAME,
        "SecurityCredential": pwd[0],
        "CommandID": "BusinessPayment",
        "SenderIdentifierType": int(SHORT_CODE),
        "RecieverIdentifierType": int(data["reciever"]),
        "Amount": data["amount"],
        "PartyA": int(SHORT_CODE),
        "PartyB": int(data["reciever"]),
        "primaryShortCode":SHORT_CODE,
        "receiverShortCode":data["reciever"],
        "Remarks": data['remarks'],
        "QueueTimeOutURL": data["result_url"],
        "ResultURL": data["result_url"],
        "AccountReference": data["reference"],
        "paymentRef":data["reference"],
        
    }

    response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/b2b/v1/paymentrequest',
                                headers=headers, data=json.dumps(payload))
    if response.status_code >= 200 and response.status_code < 300:
        try:
            return dict(response.json())
        except Exception as e:
            pass
    print(response.json())
    return dict({'message': response.json()['errorMessage'] if response.json().get('errorMessage') else 'Failed to initiate request with code '+str(response.status_code)})
