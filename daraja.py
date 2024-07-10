import payment

payment.SHORT_CODE = "3009751"
payment.PASSKEY = "a7921.222Z"#"bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
payment.CONSUMER_SECRET = "ptuHYmqLZiZkEIAR"
payment.CONSUMER_KEY = "vtC1syqw3OVAnCguu6FJArG9eNa8u2ZC"
payment.ACCOUNT_TYPE = "PAYBILL"  # Set to TILL to use BuyGoods instead of Pay Bill
payment.APP_USERNAME = "amtechaf"

async def stk(data,token):
	details = await payment.trigger_stk_push(phone_number=data['phone'], amount=data['amount'], callback_url=data['callback'],
                                   description=data['description'],
                                   account_ref=data['reference'],token=token)
	print(details);return details

def getToken():
    return payment.get_token()
	
async def query(data,token):
	details = await payment.query_stk_push(checkout_request_id=data['checkout_id'],token=token)
	print(details);return details
    
async def trans_query(data,token):
    details = await payment.query_transaction(data['transaction_id'],data['result_url'],token=token)
    print(details)
    return details

async def account_balance(data,token):
    details = await payment.query_balance(data['result_url'],token=token)
    return details
    
async def b2c(data,token):
    details = await payment.business_to_customer(data,token=token)
    return details

async def b2b(data,token):
    details = await payment.business_to_business(data,token=token)
    return details
