import sys
from flask import Flask, request,make_response  ,session,render_template,jsonify
import os
from flask_cors import CORS

# Determine the base path for files
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)


from modules import *
from models import * 
from datetime import datetime,timedelta,timezone
from controllers import *
import json
from daraja import *
from text import *
app = Flask(__name__)

app.secret_key = 'ussd'



CORS(app)

response = ""

@app.route("/home")
def home():
    action = request.args.get('action')
    actions = [
        {"name":"stk-push","data":["phone","amount","callback","description","reference"],"description":"Initiate an STK push to a users mobile phone requesting them to validate a transaction"},
        {"name":"stk-query","data":["checkout_id"],"description":"Query the status of a transaction inititated by stk push"},
        {"name":"account-balance","data":["result_url"],"description":"Request account balance of your account"},
        {"name":"transaction-status","data":["transaction_id","result_url"],"description":"Query the status of a lipa na mpesa transaction"},
        {"name":"b2c","data":["result_url","amount","remarks","occassion","phone"],"description":"Initiate a business to customer checkout to transfer funds"},
        {"name":"b2b","data":["result_url","amount","remarks","reference","reciever"],"description":"Initiate a business to bussiness transfer of funds"}
    ]
    selected = None
    if action:
        for act in actions:
            if act["name"] == action:
                selected = act
    
    return render_template("index.html",actions=actions,action=action,selected=selected)

@app.route("/result",methods=['POST','GET'])
async def result_url():
    session["access_token"] = None
    data = request
    print(data,data.json)
    return {"success":True,"ResultCode":0,"ResultDesc":"success"}

@app.route("/daraja",methods=['POST'])
async def daraja():
    if session.get("access_token") == None:
        session["access_token"] = getToken()
        session["access_token"]["time"] = datetime.now()+timedelta(int(session["access_token"]['expires_in']))
    #print(session["access_token"])
    if session["access_token"]["time"]  == None :
        session["access_token"] = getToken()
        session["access_token"]["time"] = datetime.now()+timedelta(int(session["access_token"]['expires_in']))
    response = {}
    #if response.get('message') == 'Invalid Access Token':
    #    access_token["time"] = None
    data = request.json
    action = data.get("action")
    app_id = data.get("app_id")
    
    if app_id != None:
        app = await API.find(app_id)
        if app == None:
            return json.dumps({"message":"App not found","success":False})
    else:
        app = None
    #    return json.dumps({"message":"App not specified","success":False})
    print("action",data)
    if action == None:
        return json.dumps({"success":True,"access_token":session["access_token"]["access_token"]})
    elif action == "stk-push":
        response = await stk(
            {"phone":data.get("phone"),"amount":data.get("amount"),
            "callback":data.get("callback"),"description":data.get("description"),
            "reference":data.get("reference")
            },token=session["access_token"]["access_token"],
            app = app
        )
    elif action == "stk-query":
        response = await query(
            {"checkout_id":data.get("checkout_id")},
            token = session["access_token"]["access_token"],
            app = app
        )
    elif action == "account-balance":
        print(session["access_token"]["access_token"])
        response = await account_balance(
            {"result_url":data.get("result_url")},#data.get("result_url")},
            token=session["access_token"]["access_token"],
            app = app
        )

    elif action == "transaction-status":
        response = await trans_query({"transaction_id":data.get('transaction_id'),"result_url":data.get('result_url')},
            token=session["access_token"]["access_token"],
            app = app
        )

    elif action == "b2c":
        response = await b2c({
            "result_url":data.get("result_url"),"amount":data.get("amount"),
            "remarks":data.get("remarks"),"occassion":data.get("occassion"),
            "phone":data.get("phone")
        },token=session["access_token"]["access_token"],app = app)
    elif action == "b2b":
        response = await b2b({
            "result_url":data.get("result_url"),"amount":data.get("amount"),
            "remarks":data.get("remarks"),"reference":data.get("reference"),
            "reciever":data.get("reciever")
        },token=session["access_token"]["access_token"],app = app)
    if 'Invalid Access Token' in str(response.get('message')):
        print("response",response.get("message"))
        session["access_token"] = None
    #print("response")
    return json.dumps(response)

def find_before_hash(ls):
    index_of_00 = -1
    index_of_hash = -1
    for i in range(len(ls)):
        if ls[i] == '00':
            index_of_00 = i
        if ls[i] == '#':
            index_of_hash = i
    
    if index_of_00 != -1:
        ls[index_of_00] = ''
        ls = ls[index_of_00:]
    if index_of_hash != -1:
        ss = []
        ln = 0
        for l in ls:
            if l != '#':
                ss.append(l)
            else:
                ln += 1
        return ss

@app.route("/message",methods=['POST'])
def send_text():
    data = request.json
    print("send=>",data)
    if data.get("phone"):
        phone = data.get("phone").rstrip()
        if phone.startswith('0'):
            phone =  '254' + phone[1:]
        Text.get_code(phone,code=data.get("message"))
    return jsonify({"success":True})


@app.route('/', methods=['POST','GET'])
async def ussd_callback():
    global user_state
    response = ''
    #text = request.args.get("text")
    text = request.args.get("text")
    session_id = request.args.get("session_id")
    #print("request",request.values)
    if not session_id:
        #session_id = request.json.get("session_id", None)
        session_id = request.values.get("session_id",None)
        text = request.values.get("text","")
        #service_code = request.json.get("service_code", None)
        #phone_number = request.values.get("phoneNumber", None)
        #text = request.json.get("ussd_string", "")
    text = text.strip()
    text_array = text.split('*')
    if session_id not in user_state:
        user_state[session_id] = {}
        if text_array[0] == '101' or text_array[0] == '':
            user_state[session_id]["current_array"] = ['']
            text_array[0] = ''
    
    
    
    #text_array = replace_and_slice(text_array)
    
    #if len(text_array) > 1 and text_array[0] == '101':
    #text_array = text_array[1:]
    if  user_state[session_id].get("current_state") != None:
        if len(user_state[session_id]["current_array"])> 1:
            user_state[session_id]["previous_state"]  = user_state[session_id]["current_state"]
            user_state[session_id]["current_state"] = text_array[-1]
            user_state[session_id]["current_array"] = text_array
        else:
            user_state[session_id]["current_array"] = text_array
    else:   
        user_state[session_id]["current_state"] = text_array[-1]
        user_state[session_id]["previous_state"]  = None
        if text_array[-1] != '#':
            user_state[session_id]["current_array"] = text_array

   
    text_array = user_state[session_id]["current_array"]
    if user_state[session_id]["current_state"]  == 'q' or text_array[-1] == 'q': #len(text_array) >= 1 and text_array[-1] == 'q':
        user_state[session_id] = {}
        return 'END Completed Session.\n'
    if user_state[session_id]["current_state"] == '#' or text_array[-1] == '#':
        text_hash = find_before_hash(user_state[session_id]["current_array"])
        #print("sliced=>",text_hash)
        user_state[session_id]["current_state"] = user_state[session_id]["previous_state"]
        user_state[session_id]["previous_state"] = text_hash[-2]
        user_state[session_id]["current_array"] = text_hash[:-1]
        text_array = user_state[session_id]["current_array"]
    
    if len(text_array) == 1 and text_array[0] == '101' or len(text_array) == 1 and text_array[0] == "":#text == "" or text_array[0] == '101':
        if user_state[session_id].get('user') != None:#session.get("user") != None:
            #text_array[0] = '2'
            #text_array[1] = user_state[session_id]['user']['IDNo']
            pass
        else:
            #user_state[session_id]["current_array"] = ['100']
            response = home_menu()
            return response
    
    
    print("text=>",user_state[session_id]["current_array"],text_array)
    if len(text_array) >= 1 and text_array[0] == '' or len(text_array) >= 1 and text_array[0] == '101':
        text_array = text_array[1:]
    if len(text_array) == 1 and text_array[0] == '1':
        text_array[0] = "1.1"
        
    elif len(text_array) >= 1 and text_array[0] == '2':
        text_array[0] = "2.1"
    
    #if user_state[session_id]["current_state"] == '1':#text_array[0] == '1':
    #    response = await registerMember(text_array)
    if len(text_array) == 1 and text_array[0] == '1.1':
        response = main_menu()
        return response
    #elif text_array[0] == "2.1":
    #    response = admin_menu()
    #    return response
    
    #if len(text_array) > 1 and text_array[0] == '1':
        
    #    text_array = text_array[1:]
    elif len(text_array) > 1 and text_array[0] == '2':
        text_array[1] = "2."+text_array[1]
        #text_array = text_array[1:]
    print("current=>",text_array)
    if text_array[0] == '1':
        if len(text_array) > 2 and text_array[1] != '2':
            if user_state[session_id].get('user') == None:
                member = await Members.login(text_array[2]) 
                if member == None:
                    response = nouser()
                    return response
                print("date=>",member['memberwithdrawaldate'],str(member['memberwithdrawaldate']) == '1900-01-01 00:00:00')
                if str(member['memberwithdrawaldate']) == '1900-01-01 00:00:00':
                    member['memberwithdrawaldate'] = None
                if member['memberwithdrawaldate'] != None:
                    response = inactiveuser()
                    return response
                user_state[session_id]['user'] = member
        
        if len(text_array) == 2:
            response = "CON Enter User ID No\n"
        elif len(text_array) == 3:
            if user_state[session_id].get('user') == None:
                member = await Members.login(text_array[2])
                if member == None:
                    response = nouser()
                    return response 
                user_state[session_id]['user'] = member
            else:
                member = user_state[session_id]['user']
            print("pin",user_state[session_id]['user']['PIN'])  
            if user_state[session_id]['user']['PIN'] != '' and user_state[session_id]['user']['PIN'] != None:
                response = 'CON Enter PIN\n'
            else:
                response = 'CON Set New PIN\n'
        elif len(text_array) == 4:
            PIN = text_array[3]
            if len(PIN) != 4:
                response = 'CON Invalid Pin (Must be 4 digits).\n'
                response += '00. Main Menu\nq.Exit\n'
                return response
            if user_state[session_id]['user']['PIN'] != '' and user_state[session_id]['user']['PIN'] != None:
                if user_state[session_id]['user']['PIN'] != PIN:
                    response = 'CON Invalid Pin.\n'
                    response += '00. Main Menu\nq.Exit\n'
                    return response
            if user_state[session_id]['user']['PIN'] == '' or user_state[session_id]['user']['PIN'] == None:
                user_state[session_id]['user']['PIN'] = PIN
                await Members.update(user_state[session_id]['user'])
            member = user_state[session_id]['user']
            response = f"CON You are logged in : {member['MemberNo']}.\n"
            response += '1. Add Beneficiary\n'
            response += '2. View Beneficiary\n'
            response += '3. Loans Application\n'
            #response += '4. Transfers & Offsetting\n'
            #response += '5. Transaction Management\n'
            response += '4. Loan\\Shares Enquiries\n'
            response += '5. Membership Withdrawal\n'
            response += '6. My Account\n'
            response += '00. Main Menu\nq.Exit\n'
        
        elif len(text_array) > 4:
            #print("here",text_array)
            if text_array[4] == '1':
                total_percent = await Beneficiaries.get_percent(user_state[session_id]['user'])
                if total_percent >= 100:
                    response = f'CON Can not add Beneficiary, Total assigned percentage {total_percent}.\n#.Previous Menu\n'
                    return response
                response = await addBeneficiary(text_array[1:],user=user_state[session_id]['user'],session_id=session_id,total=total_percent)

            elif text_array[4] == '2':
                if len(text_array) == 5:
                    beneficiaries = await Beneficiaries.find(user_state[session_id]['user'])
                    response = 'CON Viewing Beneficiaries\n'
                    index = 0
                    for bn in beneficiaries:
                        index += 1
                        response += f'{index}.{bn['KinNames']} - {bn['IDNo']} ({bn['Percentage']})%\n' 
                    response += '\n'
                    response += '# Previous Menu\n00.Main Menu\n'
                
                else:
                    response = "END Invalid input."
            elif text_array[4] == '3':
                if len(text_array) == 5:
                    response = loansProcessing()
                if len(text_array) > 5:
                    if text_array[5] == '1':#loans application
                        response = await loanApplication(text_array[1:],initial=5,user=user_state[session_id]['user'],session_id=session_id)
                    elif text_array[5] == '2':#loans guarantors
                        response = await loanGuarantors(text_array[1:],initial=5,user=user_state[session_id]['user'],session_id=session_id)
                    #elif text_array[4] == '3':#loans appraisals
                    #    response = loanAppraisals(text_array,initial=5)
                    #"""
                    #elif text_array[4] == '4':#loans endorsements
                    #    response = 'CON Not Available\n00.Main Menu\n'
                    #elif text_array[4] == '5':#payment posting
                    #    response = receiptPosting(text_array,initial=5)
                    #elif text_array[4] == '6':#loans schedule
                    #    response = loanSchedule(text_array,initial=5)
                    #"""
                    elif text_array[5] == '3':#delete loan
                        response = await loanDelete(text_array[1:],initial=5,user=user_state[session_id]['user'],session_id=session_id)
                    #elif text_array[4] == '5':#shares/saving adjustment
                    #    response = 'CON Not Available\n00.Main Menu\n'
                    else:
                        response = 'END Invalid Input'
            #"""
            #elif text_array[3] == '4':
            #    if len(text_array) == 4:
            #        response = transfersOffseting()
            #    if len(text_array) > 4:
            #        if text_array[4] == '1':#Share transfers
            #            response  = shareTansfers(text_array,initial=5)
            #        elif text_array[4] == '2':#share to loan offseting
            #            response = shareLoanOffset(text_array,initial=5)
            #       
            #        else:
            #            response = 'END Invalid Input'
            #elif text_array[3] == '5':#Transaction Management
            #    if len(text_array) == 4:
            #        response = transactionManagement(text_array)
            #    if len(text_array) > 4:
            #        if text_array[4] == '1':#receipt Posting
            #            response = receiptPosting(text_array,initial=5)
            #        elif text_array[4] == '2':#my Transactions
            #            response = myTransactions(text_array)
            #"""
            elif text_array[4] == '4':#Enquiries
                if len(text_array) == 5:
                    response = Enquiries(text_array[1:])
                if len(text_array) > 5:
                    if text_array[5] == '1':#My Shares
                        response = await myShares(text_array[1:],initial=5,user=user_state[session_id]['user'],session_id=session_id)
                    if text_array[5] == '2':#My Loans
                        response = await myLoans(text_array[1:],initial=5,user=user_state[session_id]['user'],session_id=session_id)
                    if text_array[5] == '3':#My Members if company
                        response = myMembers(text_array[1:],initial=5)
                    if text_array[5] == '4':#Shares/Savings Variations
                        response = myMembersShares(text_array[1:],initial=5)
            elif text_array[4] == '5':
                if len(text_array) >= 5:
                    response = await MemberWithdrawal(text_array[1:],initial=4,user=user_state[session_id]['user'],session_id=session_id)
            elif text_array[4] == '6':
                response = 'CON Your Account Details.\n'
                response += f'Member No: {user_state[session_id]['user']['MemberNo']}\nID No: {user_state[session_id]['user']['IDNo']}\n'
                response += f'Surname: {user_state[session_id]['user']['Surname']}\nNames: {user_state[session_id]['user']['OtherNames']}\n'
                response += f'SEX: {user_state[session_id]['user']['Sex']}\nDOB: {str(user_state[session_id]['user']['DOB']).split(" ")[0]}\n'
                response += f'Mobile: {user_state[session_id]['user']['MobileNo']}\nSACCO: {user_state[session_id]['user']['CompanyName']}\n'
                response += '#.Previous Menu\n00.Main Menu\nq.Exit\n'   
            else:
                response = "END Invalid input."
    elif text_array[0] == '2':
        
        response = await resetPassword(text_array,initial = 1)
        return response            
    elif text_array[0] == '2.1':
        response = await admin_home(text_array,session_id=session_id)
    #elif text_array[0] == '4':
    #    response = await registerAgent(text_array)
    else:
        response = 'END Invalid Input.'

    
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    app.run(host="0.0.0.0", port=port )
