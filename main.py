
from flask import Flask, request,make_response  ,session,render_template
import os
from flask_cors import CORS
from modules import *
from models import * 
from datetime import datetime,timedelta,timezone
from controllers import *
import json
from daraja import *
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
        {"name":"b2c","data":["result_url","amount","remarks","occasion","phone"],"description":"Initiate a business to customer checkout to transfer funds"},
        {"name":"b2b","data":["result_url","amount","remarks","reference","reciever"],"description":"Initiate a business to bussiness transfer of funds"}
    ]
    selected = None
    if action:
        for act in actions:
            if act["name"] == action:
                selected = act
    
    return render_template("index.html",actions=actions,action=action,selected=selected)

@app.route("/result",methods=['POST'])
async def result_url():
    data = request.json
    print(data)
    return {"success":True}

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
    print("action",action)
    if action == None:
        return json.dumps({"success":True,"access_token":session["access_token"]["access_token"]})
    elif action == "stk-push":
        response = await stk(
            {"phone":data.get("phone"),"amount":data.get("amount"),
            "callback":data.get("callback"),"description":data.get("description"),
            "reference":data.get("reference")
            },token=session["access_token"]["access_token"]
        )
    elif action == "stk-query":
        response = await query(
            {"checkout_id":data.get("checkout_id")},
            token = session["access_token"]["access_token"]
        )
    elif action == "account-balance":
        response = await account_balance(
            {"result_url":data.get("result_url")},
            token=session["access_token"]["access_token"]
        )

    elif action == "transaction-status":
        response = await trans_query({"transaction_id":data.get('transaction_id'),"result_url":data.get('result_url')},
            token=session["access_token"]["access_token"]
        )

    elif action == "b2c":
        response = await b2c({
            "result_url":data.get("result_url"),"amount":data.get("amount"),
            "remarks":data.get("remarks"),"occassion":data.get("occassion"),
            "phone":data.get("phone")
        },token=session["access_token"]["access_token"])
    elif action == "b2b":
        response = await b2b({
            "result_url":data.get("result_url"),"amount":data.get("amount"),
            "remarks":data.get("remarks"),"reference":data.get("reference"),
            "reciever":data.get("reciever")
        },token=session["access_token"]["access_token"])
    if 'Invalid Access Token' in str(response.get('message')):
        print("response",response.get("message"))
        session["access_token"] = None
    return json.dumps(response)

@app.route('/', methods=['POST','GET'])
async def ussd_callback():
    response = ''
    #print("request",request.values)
    session_id = request.json.get("session_id", None)
    service_code = request.json.get("service_code", None)
    #phone_number = request.values.get("phoneNumber", None)
    text = request.json.get("ussd_string", "default")
    text = request.json.get('ussd_string', '').strip()
    
    text_array = text.split('*')
    
    text_array = replace_and_slice(text_array)
    if len(text_array) > 1 and text_array[0] == '101':
        text_array = text_array[1:]

    print("text",text_array)
    if len(text_array) >= 1 and text_array[-1] == 'q':
        return 'END Completed Session.\n'
    if text == "" or text_array[0] == '101':
        if session.get("user") != None:
            text_array[0] = '2'
            text_array[1] = session['user']['IDNo']
        else:
            response = main_menu()
            return response
    if text_array[0] == '1':
        response = await registerMember(text_array)
    elif text_array[0] == '2':
        if len(text_array) > 1:
            if session.get('user') == None:
                member = await Members.login(text_array[1]) 
                if member == None:
                    response = nouser()
                    return response
                print("date=>",member['memberwithdrawaldate'],str(member['memberwithdrawaldate']) == '1900-01-01 00:00:00')
                if str(member['memberwithdrawaldate']) == '1900-01-01 00:00:00':
                    member['memberwithdrawaldate'] = None
                if member['memberwithdrawaldate'] != None:
                    response = inactiveuser()
                    return response
                session['user'] = member
        if len(text_array) == 1:
            response = "CON Enter User ID No\n"
        elif len(text_array) == 2:
            if session.get('user') == None:
                member = await Members.login(text_array[1])
                if member == None:
                    response = nouser()
                    return response 
                session['user'] = member
            else:
                member = session['user']
                
            if session['user']['PIN'] != '' and session['user']['PIN'] != None:
                response = 'CON Enter PIN\n'
            else:
                response = 'CON Set New PIN\n'
        elif len(text_array) == 3:
            PIN = text_array[2]
            if len(PIN) != 4:
                response = 'CON Invalid Pin (Must be 4 digits).\n'
                response += '00. Main Menu\nq.Exit\n'
                return response
            if session['user']['PIN'] != '' and session['user']['PIN'] != None:
                if session['user']['PIN'] != PIN:
                    response = 'CON Invalid Pin.\n'
                    response += '00. Main Menu\nq.Exit\n'
                    return response
            if session['user']['PIN'] == '' or session['user']['PIN'] == None:
                session['user']['PIN'] = PIN
                await Members.update(session['user'])
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
        
        elif len(text_array) > 3:
            #print("here",text_array)
            if text_array[3] == '1':
                response = await addBeneficiary(text_array,user=session['user'])

            elif text_array[3] == '2':
                if len(text_array) == 4:
                    beneficiaries = await Beneficiaries.find(session['user'])
                    response = 'CON Viewing Beneficiaries\n'
                    index = 0
                    for bn in beneficiaries:
                        index += 1
                        response += f'{index}.{bn['KinNames']} - {bn['IDNo']} ({bn['Percentage']})%\n' 
                    response += '\n'
                    response += '# Previous Menu\n00.Main Menu\n'
                
                else:
                    response = "END Invalid input."
            elif text_array[3] == '3':
                if len(text_array) == 4:
                    response = loansProcessing()
                if len(text_array) > 4:
                    if text_array[4] == '1':#loans application
                        response = await loanApplication(text_array,initial=5,user=session['user'])
                    elif text_array[4] == '2':#loans guarantors
                        response = await loanGuarantors(text_array,initial=5,user=session['user'])
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
                    elif text_array[4] == '3':#delete loan
                        response = await loanDelete(text_array,initial=5,user=session['user'])
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
            elif text_array[3] == '4':#Enquiries
                if len(text_array) == 4:
                    response = Enquiries(text_array)
                if len(text_array) > 4:
                    if text_array[4] == '1':#My Shares
                        response = await myShares(text_array,initial=5,user=session['user'])
                    if text_array[4] == '2':#My Loans
                        response = await myLoans(text_array,initial=5,user=session['user'])
                    if text_array[4] == '3':#My Members if company
                        response = myMembers(text_array,initial=5)
                    if text_array[4] == '4':#Shares/Savings Variations
                        response = myMembersShares(text_array,initial=5)
            elif text_array[3] == '5':
                if len(text_array) >= 4:
                    response = await MemberWithdrawal(text_array,initial=4,user=session['user'])
            elif text_array[3] == '6':
                response = 'CON Your Account Details.\n'
                response += f'Member No: {session['user']['MemberNo']}\nID No: {session['user']['IDNo']}\n'
                response += f'Surname: {session['user']['Surname']}\nNames: {session['user']['OtherNames']}\n'
                response += f'SEX: {session['user']['Sex']}\nDOB: {str(session['user']['DOB']).split(" ")[0]}\n'
                response += f'Mobile: {session['user']['MobileNo']}\nSACCO: {session['user']['CompanyName']}\n'
                response += '#.Previous Menu\n00.Main Menu\nq.Exit\n'   
            else:
                response = "END Invalid input."
                
    elif text_array[0] == '3':
        response = registerCompany(text_array)
    elif text_array[0] == '4':
        response = await registerAgent(text_array)
    else:
        response = 'END Invalid Input.'

    
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port,debug=True )
