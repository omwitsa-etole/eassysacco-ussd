import payment

payment.SHORT_CODE = "3009751"
payment.PASSKEY = "6352676792252912b8ceb1a77f3474b0ddf1527290223acc1636d9be5f962a4f"
payment.CONSUMER_SECRET = "VlrxOABGSaguGVM6GHCrjG170ODEuMKae2lVP2VxCGohQj51r1GinDYYg9Kw9FwL"
payment.CONSUMER_KEY = "zU6A23DSGUtog9n79cYDsF9Wljb4MtbjJyNrOcJ1pUGtYMDi"
payment.ACCOUNT_TYPE = "PAYBILL"  # Set to TILL to use BuyGoods instead of Pay Bill
payment.APP_USERNAME = "PSIGEI"
payment.PASSWORD = b"a7921.222Z"

async def stk(data,token,app=None):
    global payment
    payment.SHORT_CODE = app['ShortCode']
    payment.PASSKEY = app['PassKey']
    payment.APP_USERNAME = app['ApiUser']
    payment.PASSWORD = app['ApiPassword'].encode()

    details = await payment.trigger_stk_push(phone_number=data['phone'], amount=data['amount'], callback_url=data['callback'],
                           description=data['description'],
                           account_ref=data['reference'],token=token)
    print(details);return details

def getToken():
    return payment.get_token()
	
async def query(data,token,app=None):
    global payment
    payment.SHORT_CODE = app['ShortCode']
    payment.PASSKEY = app['PassKey']
    payment.APP_USERNAME = app['ApiUser']
    payment.PASSWORD = app['ApiPassword'].encode()
    details = await payment.query_stk_push(checkout_request_id=data['checkout_id'],token=token)
    print(details);return details
    
async def trans_query(data,token,app=None):
    global payment
    payment.SHORT_CODE = app['ShortCode']
    payment.PASSKEY = app['PassKey']
    payment.APP_USERNAME = app['ApiUser']
    payment.PASSWORD = app['ApiPassword'].encode()
    details = await payment.query_transaction(data['transaction_id'],data['result_url'],token=token)
    print(details)
    return details

async def account_balance(data,token,app=None):
    global payment
    payment.SHORT_CODE = app['ShortCode']
    payment.PASSKEY = app['PassKey']
    payment.APP_USERNAME = app['ApiUser']
    payment.PASSWORD = app['ApiPassword'].encode()
    details = await payment.query_balance(data['result_url'],token=token)
    return details
    
async def b2c(data,token,app=None):
    global payment
    payment.SHORT_CODE = app['ShortCode']
    payment.PASSKEY = app['PassKey']
    payment.APP_USERNAME = app['ApiUser']
    payment.PASSWORD = app['ApiPassword'].encode()
    details = await payment.business_to_customer(data,token=token)
    return details

async def b2b(data,token,app=None):
    global payment
    payment.SHORT_CODE = app['ShortCode']
    payment.PASSKEY = app['PassKey']
    payment.APP_USERNAME = app['ApiUser']
    payment.PASSWORD = app['ApiPassword'].encode()
    details = await payment.business_to_business(data,token=token)
    return details
