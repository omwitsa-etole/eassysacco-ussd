import random
import requests
import json
import smtplib, ssl
import os
from twilio.rest import Client
class Text:
    SID = "1234"
    TOKEN = "1234"
    TWILIO_NUMBER = "+19786072862"
    client = Client(SID,TOKEN)

    @staticmethod
    async def get_code(number,code=random.randint(1000,9999)):
        recipient_number = number if "+" in str(number) else "+"+str(number)
        message = Text.client.messages.create(
            body=str(code),
            from_=Text.TWILIO_NUMBER,
            to=recipient_number
        )
        print("Message sent :",json.dumps(message))
        if message.sid:
            return True
        return False
