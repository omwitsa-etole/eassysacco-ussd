
from flask import Flask, request,make_response  ,session
import os
from flask_cors import CORS
from modules import *
from models import * 
from datetime import datetime
from controllers import *
app = Flask(__name__)

app.secret_key = 'ussd'

CORS(app)

response = ""

def replace_and_slice(ls):
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
        print("ss=>",ss)
        last = ss[-1]
        ss = ss[:-ln]
        #if last != '#':
            #ss[-1] = last
        return ss
        #ls[index_of_hash] = ''
    if ls[-1] == '0' and len(ls) > 3:
        ss = []
        for k in range(1,3):
            ss.append(ls[k-1])
        #ss.append('0')
        return ss
    
    return ls

def nouser():
    response = 'CON Account not Found.\n'
    response += '00. Main Menu\nq.Exit\n'
    return response

def inactiveuser():
    response = 'CON You have deactivated your Membership.\nContact support for reinstatement.\n'
    response += '00. Main Menu\nq.Exit\n'
    return response


@app.route('/', methods=['POST', 'GET'])
async def ussd_callback():
    response = ''
    #print("request",request.values)
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    text = request.values.get('text', '').strip()
    
    text_array = text.split('*')
    
    text_array = replace_and_slice(text_array)
    if len(text_array) > 1 and text_array[0] == '':
        text_array = text_array[1:]

    print("text",text_array)
    if len(text_array) >= 1 and text_array[-1] == 'q':
        return 'END Completed Session.\n'
    if text == "" or text_array[0] == '':
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
                    elif text_array[4] == '3':#loans appraisals
                        response = loanAppraisals(text_array,initial=5)
                    #"""
                    #elif text_array[4] == '4':#loans endorsements
                    #    response = 'CON Not Available\n00.Main Menu\n'
                    #elif text_array[4] == '5':#payment posting
                    #    response = receiptPosting(text_array,initial=5)
                    #elif text_array[4] == '6':#loans schedule
                    #    response = loanSchedule(text_array,initial=5)
                    #"""
                    elif text_array[4] == '4':#delete loan
                        response = loanDelete(text_array,initial=5)
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
                response += f'SEX: {session['user']['Sex']}\nDOB: {session['user']['DOB'].split(" ")[0]}\n'
                response += f'Mobile: {session['user']['MobileNo']}\nSACCO: {session['user']['CompanyCode']}\n'
                response += '#.Previous Menu\n00.Main Menu\nq.Exit\n'   
            else:
                response = "END Invalid input."
                
    elif text_array[0] == '3':
        response = registerCompany(text_array)
    elif text_array[0] == '4':
        response = registerAgent(text_array)
    else:
        response = 'END Invalid Input.'

    
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host="0.0.0.0", port=port )
