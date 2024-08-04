from datetime import datetime
from models import *
from modules import * 
from flask import session
import aiohttp
import asyncio
import requests

user_state = {}

API_URL = "http://localhost:8081"

async def send_post(session, url, data):
    try:
        requests.post(url, json=data) 
    except Exception as e:
        print(f"An error occurred: {e}")

def get_age(birthdate_str):
    birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
    today = datetime.today()
    age = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    return int(age)


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
        #if ss[-1] != last:
            #pass#ss[-1] = last
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
    
def main_menu():
    response = "CON Welcome to our service\n"
    #response += "1. Register new Member\n"
    response += "1. Login \n"
    response += "2. Forgot Password\n"
    #response += "3. Company Registration\n"
    #response += '4. Agent Recruitment\n'
    response += 'q.Exit\n'
    return response
    
async def Agent_menu(text_array,initial=0,session_id=None):
    global user_state
    agent = user_state[session_id].get("agent")
    response = f"CON Agent: {agent["Names"]}"
    if len(text_array) > initial:
        if text_array[initial] == "1":
            response = await registerMember(text_array[initial:],session_id=session_id)
        else:
            response += "\nNot yet available.\n"
    else:
        response += "\n1.Register Member\n"
        response += "2.Reset Password\n"
    return response
async def admin_home(text_array,initial = 1,session_id=None):
    response = "CON COMPANY"
    global user_state
    print("array",text_array)
    if len(text_array) == initial:
        response += "\n1.Agent Login\n"
    else:
        if text_array[1] == "1":
            if len(text_array) == initial+1:
                response += "\nEnter IDNo \n"
            if len(text_array) == initial+2:
                response += "\nEnter Pin\n"
        
        if len(text_array) >= initial+3:
            idNo = text_array[initial+1]
            pinNo = text_array[initial+2]
            if user_state[session_id].get("agent") == None:
                agent = await Agents.find(idNo)
                user_state[session_id]["agent"] = agent
            else:
                agent = user_state[session_id]["agent"]
            #print("agent=>",agent)
            if agent == None:
                response += "\nIncorrect credentials. Not found\n"
                return response
            
            if agent["PIN"] == None:
                user_state[session_id]["agent"]["PIN"] = pinNo
                agent = user_state[session_id]["agent"]
                await Agents.updatePIN(agent)
            else:
                if agent["PIN"] != pinNo:
                    response = "END Invalid Login Password\n"
                    return response
            if len(text_array) >= initial+3:
                response = await Agent_menu(text_array,initial=initial+3,session_id=session_id)
                
        
    response += "#.Previous Menu\n00.Main Menu\n"
    return response
def admin_menu():
    response = "CON Welcome to our service\n"
    #response += "1. Register new Member\n"
    response += "1.Admin Login \n"
   # response += "2. Regiter Agent\n"
    #response += "3. Company Registration\n"
    #response += '4. Agent Recruitment\n'
    response += 'q.Exit\n'
    return response
def home_menu():
    response = "CON Welcome to EassyUSSD, Select to Continue\n"
    response += "1.Member\n"
    response += "2.Agent\nq.Exit\n"
    return response
async def registerAgent(text_array):
    if len(text_array) == 1:
        response = 'CON Enter Staff Names'
    elif len(text_array) == 2:
        response = 'CON Enter Company Code'
    elif len(text_array) == 3:
        company = await Companies.find(company_number)
        if company == None:
            return 'END No Company found \n Try again '
        response = 'CON Enter ID No.'
    elif len(text_array) == 4:
        response = 'CON Enter Gender(Male,Female).'
    elif len(text_array) == 5:
        response = 'CON Enter Mobile No.'
    elif len(text_array) == 6:
        response = 'CON Enter Address.'
    elif len(text_array) == 7:
        response = 'CON Enter Occupation.'
    elif len(text_array) == 8:
        response = 'CON Select Station.\n'
        response += '1.Nairobi\n'
    elif len(text_array) == 9:
        station = text_array[8]
        if station == '1':
            station = 'Nairobi'
        else:
            response = 'END Invalid Input\n'
        names = text_array[1]
        company_number = text_array[2]
        id_no = text_array[3]
        gender = text_array[4]
        print(gender,gender.lower())
        if gender.lower() != 'male' and gender.lower() != 'female':
            return 'END Invalid gender provided\n'
        mobile_no = text_array[5]
        print(mobile_no)
        if len(mobile_no) < 9:
            return 'END Invalid Phone number'
        
        address = text_array[6]
        occupation = text_array[7]
        print("adding agent",station,names,company_number,id_no,gender,mobile_no,address,occupation)
        response = 'CON Details added successfully\n00.Main Menu\nq.Exit\n'
    else:
        response = "END Invalid input."
    return response
async def registerMember(text_array,session_id=None):
    global user_state
    agent = user_state[session_id]["agent"]
    """if len(text_array) == 1:
            
        response = "CON Enter Company Code"
    elif len(text_array) == 2:
        company_c = text_array[1]
        company = await Companies.find(company_c)
        if company == None:
            response = 'END Could not find company try again.\n'
            return response
        response = "CON Enter Agent IDNo"
    elif len(text_array) == 3:
        agent_ref = text_array[2]
        agent = await Agents.find(agent_ref)
        if agent == None:
            response = 'END Could not find Agent associated with ID.\n'
            return response
        response = "CON Enter county of residence."
    """
    if len(text_array) == 1:
        response = "CON Enter county of residence."
    elif len(text_array) == 2:
        
        response = "CON Enter phone number"
    elif len(text_array) == 3:
        
        response = "CON Enter surname"
    elif len(text_array) == 4:
        
        response = "CON Enter other names"
    elif len(text_array) == 5:
    
        response = "CON Enter date of birth (YYYY-MM-DD)"
    elif len(text_array) == 6:
        
        response = "CON Enter ID number"
    elif len(text_array) == 7:
        
        response = "CON Enter your Gender (Male,Female)\n"
    elif len(text_array) == 8:
        
        company_code = agent["CompanyCode"]
        agent = agent["IdNo"]
        county = text_array[1]
        phone = text_array[2]
        surname = text_array[3]
        other_names = text_array[4]
        date_of_birth = text_array[5]
        id_no = text_array[6]
        gender = text_array[7].upper()
        find = await Members.login(id_no)
        if find != None:
            response = 'END Member with ID no is already registered\n'
            return response
        last = await Members.get_last(company_code,county)
        if last['MemberNo'] == None:
            response = 'END Sorry the Company does not accept new Members.\nContact the Company for support\n'
            return response
        if last['Employer'] == None:
            last['Employer'] = ""
        
        member = Member(
            MemberNo = last['MemberNo'],
            Employer = last['Employer'],
            CompanyCode = company_code,
            AgentId = agent,OtherNames = other_names,
            PhoneNo = phone,Surname = surname,
            MobileNo = phone,Age = get_age(date_of_birth),
            IDNo = id_no,StaffNo = last['MemberNo'],
            Sex = gender,DOB = date_of_birth,
            Station = county,Province = county,District=county
        )
        member = member.get()
        result = await Members.create(member)
        if result:
            print("registering",company_code,last['MemberNo'])
            response = "CON Thank you for providing details.Member added\n"
        else:
            response = "CON Could not create account, try again later.\n"
        response += "00. Main Menu\nq.Exit"
        return response
    
    else:
        response = "END Invalid input."
    return response

def registerCompany(text_array):
    response = 'CON For company registration contact info@amtechafrica.com.\n'
    response += "00. Main Menu\nq.Exit"
    return response
    if len(text_array) == 1:
        response = 'CON Enter Company Name.'
    elif len(text_array) == 2:
        response = 'CON Enter Company Phone.'
    elif len(text_array) == 3:
        response = 'CON Enter Company Email.'
    elif len(text_array) == 4:
        response = 'CON Enter Company County.'
    elif len(text_array) == 5:
        response = 'CON Enter Company SubCounty.'
    elif len(text_array) == 6:
        response = 'CON Enter Company Ward.'
    elif len(text_array) == 7:
        response = 'CON Enter Company Number of Members.'
    elif len(text_array) == 8:
        response = 'CON Enter Company Postal Address.'
    elif len(text_array) == 9:
        response = 'CON Enter Company Contact Person.'
    elif len(text_array) == 10:
        response = 'CON Enter Company Business Status.'
    elif len(text_array) == 11:
        print('regsitering company',text_array)
        response = 'CON Company details saved.\n'
        response += "00. Main Menu\nq.Exit"
    else:
        response = 'END Invalid Input.'

    return response

def is_integer(input_string):
    try:
        int(input_string)
        return True
    except ValueError:
        return False

def is_string(input_string):
    return all(not char.isdigit() for char in input_string)

async def resetPassword(text_array,initial=0):
    response = "CON Password Reset"
    if len(text_array) > initial:
        if len(text_array) - initial == 1:
            response += "\nEnter Member No\n"
        else:
            id = text_array[initial]
            member_no = text_array[initial+1]
            print("resetting=>",id,member_no)
            result = await Members.login(id)
            if result == None:
                response += "\n Account could not be found, Ensure corect details and try again\n"
            else:
                if result["MemberNo"] != member_no:
                    response += "\n Member details not validated, Ensure corect details and try again\n"
                else:
                    if result["PIN"] == "" or result["PIN"] == None:
                        result["PIN"] = "Not Set, Login to Set new Password"
                    async with aiohttp.ClientSession() as session:
                        asyncio.create_task(send_post(session, API_URL+"/message", {"message":"Your Password is "+result["PIN"],"phone":result["PhoneNo"]}))
                    response += "\nRecieved password reset request, You will recieve sms shortly.\n "
    else:
        response += "\nEnter user IDNo \n"

    response += "#.Previous Menu.\nq.Exit"
    return response

async def addBeneficiary(text_array,user=None,session_id=None,total=0):

    if len(text_array) == 4:
        response = 'CON Enter KIN ID NO.'
    elif len(text_array) == 5:
        response = 'CON Enter KIN Names.'
    elif len(text_array) == 6:
        if is_string(text_array[5]) == False:
            response = f'CON Invalid input Name.\n#.Previous Menu\nq.Exit'
            return response
        response = 'CON Enter KIN Phone.'
    elif len(text_array) == 7:
        if is_string(text_array[6]) == False:
            response = f'CON Invalid input Phone.\n#.Previous Menu\nq.Exit'
            return response
        response = 'CON Enter Percentage(%).'
    elif len(text_array) == 8:
        if is_integer(text_array[7]) == False:
            response = f'CON Invalid input percentage.\n#.Previous Menu\nq.Exit'
            return response
        if int(text_array[7])+total > 100:
            response = f'CON Can not add Beneficiary, Total left percentage that can be assigned is {total-int(text_array[7])}.\n#.Previous Menu\nq.Exit'
            return response
        response = 'CON Enter Beneficiary Relationship \n(e.g child,sibling,parent,spouse).'
    elif len(text_array) == 9:
        response = 'CON Enter Other comments\n'
    elif len(text_array) == 10:
        last_no = await Beneficiaries.get_last(user['MemberNo'])
        new_kin = Beneficiary(Comments=text_array[-1],
            Relationship = text_array[-2].upper(),
            Percentage = text_array[-3],
            Phone = text_array[-4],
            KinNames = text_array[-5],IDNo = text_array[-6],
            KinNo = last_no,
            Address = '1',
            MemberNo = user['MemberNo'],
            CompanyCode = user['CompanyCode']
        )
        new_kin = new_kin.get()
        if int(new_kin['Percentage']) > 100 or int(new_kin['Percentage']) < 1:
            response = 'END invalid Percentage value'
            return response
        elif len(new_kin['IDNo']) != 8:
            response = 'END invalid IDNo provided'
            return response
        #print('beneficiary=>',new_kin,"\nLast=>",last_no)
        result = await Beneficiaries.add(new_kin)
        if result and result ==True:
            response = 'CON Added Beneficiary.'
        else:
            response = 'CON Could not add Beneficiary try again later.\n'
        response += '\n0.Home\n00.Main Menu\nq.Exit\n'
    else:
        response = "END Invalid input."

    return response
def loansProcessing():
    response = 'CON Loan Applications.\n'
    response += '1.Loan Application.\n'
    response += '2.Loan Guarantors.\n'
    #response += '3.Loan Appraisals.\n'
    #response += '4.Endorsements.\n'
    #response += '5.Payments posting\n'
    #response += '6.Loans Schedule\n'
    response += '3.Delete Loan\n'
    #response += '5.Shares\\Savings \n'
    response += '#.Previous Menu\n00.Main Menu.\n'
    return response

def transfersOffseting():
    response = 'CON Transfers and Offsetting.\n'
    response += '1.Share Transfers\n'
    response += '2.Share to Loan Offseting\n'

    response += '00.Main Menu.\n'
    return response

def transactionManagement(text_array):
    response = 'CON Transaction Management.\n'
    response += '1.Receipt Posting\\Shares\n'
    response += '2.My Transactions\n'
    response += '00.Main Menu.\n'
    return response
def Enquiries(text_array):
    response = 'CON Loan Enquiries.\n'
    response += '1.My Shares \n'
    response += '2.My Loans \n'
    #response += '3.Members in my Company\n'
    
    #response += '4.Share\\Savings Variations\n'
    response += '#.Previous menu\n00.Main Menu.\n'
    return response

async def loanApplication(text_array,initial=0,user=None,session_id=None):
    member_loan = await Members.loan(user)
    member_bal = await Members.loanBal(user)
    if member_loan == None:
        member_loan = {'contrib':{'Amount':0}}
    if member_loan.get('share') == None:
        member_loan['share'] = {'LoanToShareRatio':1}
    if member_bal == None:
        member_bal = {'balances':[],'loanBal':0}
    #print("loan=>",member_loan,"\nBalance=>",member_bal)
    loan_balance = member_bal['loanBal']
    loan_contribution = member_loan['contrib']['Amount']
    loan_amount = float(loan_contribution) - float(loan_balance)
    ratio = member_loan['share']['LoanToShareRatio']
    loan_limit = float(loan_amount)*int(ratio)
    periods = [3,6,12,18,36]
    global user_state
    global API_URL
    response = 'CON Loan Application\n'
    if len(text_array) > initial:
        if is_integer(text_array[initial]) == False:
            if is_string(text_array[5]) == False:
                response = f'CON Invalid input Amount.\n#.Previous Menu\nq.Exit'
                return response
        if user.get('selected'):
            loan_types = user['selected']
        else:
            loan_types = await Loans.get_types(user['CompanyCode'])
            user_state[session_id]['user']['selected'] = loan_types
        if float(text_array[initial]) > loan_limit:
                response += f'Applied Loan Amount {text_array[initial]} can not be greater than current limit {loan_limit}.\n#.previous Menu\n00.Main Menu\n'
                return response
        if len(text_array) - initial == 1:
            response = 'CON Select Loan type.\n'
            ind = 0
            for loan_type in loan_types:
                ind += 1
                response += f"{ind}.{loan_type['LoanType']} at {loan_type['Interest']}%\n"
            
        if len(text_array) - initial == 2:
            selected_type = int(text_array[initial-2])
            if int(selected_type) > len(loan_types):
                response += 'Invalid  Option Selected.\n'
                response += '#.Previous Menu\n00.Main Menu.\n'
                return response
            selected_type = loan_types[selected_type-1]
            #if user.get('selected_loan') == None:
                
            if loan_limit > selected_type['MaxAmount']:
                loan_limit = selected_type['MaxAmount']
            if float(text_array[initial]) > loan_limit:
                response += f'Applied Loan Amount {text_array[initial]} can not be greater than current limit {loan_limit}.\n'
            else:
                response += f'{selected_type['LoanType']} LOAN for amount {text_array[initial]} and Interest rate {selected_type['Interest']}% has been selected.\n1.Confirm\n2.Cancel\n'
        if len(text_array) - initial == 3:
            response += '\nEnter Loan Repayment Period in Months\n#.previous Menu\nq.Exit'
        if len(text_array) - initial == 4:
            if is_integer(text_array[initial-3]) == False:
                response += '\nInvalid  Repayment Period in Months\n#.previous Menu\nq.Exit'
                return response
            selected_type = int(text_array[initial-2])
            selected_type = loan_types[selected_type-1]
            if text_array[-1] == '1':
                next_no = await Loans.get_next(user,selected_type)
                new_loan = Loan(
                    LoanNo = next_no['LoanNo'],
                    Amount = text_array[initial],LoanAmt = text_array[initial],
                    LoanCode = selected_type['LoanCode'],
                    CompanyCode = selected_type['CompanyCode'],
                    Status = 1,MemberNo = user['MemberNo'],
                    RepayPeriod = int(text_array[initial-3]),
                    IdNo = user['IDNo'],
                    Interest = selected_type['Interest'],
                    id = next_no['id']
                )
                new_loan = new_loan.get()
                print("new loan=>",new_loan)
                result = await Loans.add(new_loan)
                if result and result == True:
                    async with aiohttp.ClientSession() as session:
                        asyncio.create_task(send_post(session, API_URL+"/message", {"message":"Your loan Application was successfull","phone":user["PhoneNo"]}))
                    response = 'CON Application Posted.Track Progress in Main Menu\n'
                else:
                    response = 'CON Application failed. Try again later.\n'
            else:
                response = 'CON Application has been cancelled.\n'
            response += '#.Previous Menu\n00.Main Menu.\n'
            return response
    else: 
        if loan_limit == 0:
            response += 'You current loan limit is 0 continue to grow contributions to apply for a Loan.\n'
        else:
            response += f'Max Loan Amount {loan_limit} \n Outstanding Loan Balance {loan_balance} \nEnter Amount apply for.\n\n'
    response += '#.Previous Menu\n00.Main Menu.\n'
    return response
async def loanGuarantors(text_array,initial=0,user=None,session_id=None):
    print("guarantors",text_array)
    response = 'CON Viewing Gurantors.\n'
    guarantors = await Guarantors.find(user)
    if len(text_array) > initial:
        selected = text_array[initial]
        if int(selected) > len(guarantors):
            response = 'CON Invalid Option.\n'
        selected = guarantors[int(selected)-1]
        
        response = f'CON Viewing Loan No {selected['LoanNo']}.\n'
        response += f'Guarantor : {selected['MemberNo']}\nAmount : {float(selected['Amount'])}\nBalance : {float(selected['Balance'])}'
        #response += "Unavailable"
    else:
        ind = 0
        for guarantor in guarantors:
            ind += 1
            response += f"{ind}. Loan : {guarantor['LoanNo']} - Member : {guarantor['MemberNo']}"
        
    response += '#.Previous Menu\n00.Main Menu.\n'
    return response

def loanAppraisals(text_array,initial=0):
    print("appraisails",text_array)
    response = 'CON Loan Appraisals.\nCurrently Unavailable\n#.Previous Menu\n00.Main Menu\nq.Exit\n'
    return response
    if len(text_array) > initial:
        if len(text_array)-initial == 1 and text_array[initial] == '1':
            response += 'Enter Appraisal Amount. (min. 100)\n'
        elif len(text_array)-initial == 1 and text_array[initial] == '2':
            for i in range(0,2):
                response += f'{i}.Appraisal {i}.\n'

        elif len(text_array)-initial > 1:
            if len(text_array[initial+1]) <= 2:
                loan_no = 1234
                loan_balance = 0
                max_loan = 0
                total_shares = 0
                loan_appraisal = 2000
                appraisal_status = 'Pending'
                appraisal = text_array[initial]
                response += f'Loan No. {loan_no}\nLoan Balance. {loan_balance}\nMax Loan Amount. {max_loan}\nTotal shares. {total_shares}\nApplied Appraisal Amount. {loan_appraisal}\n'
                response += f'Status. {appraisal_status} \n'
            else:
                response += f'New Application for Appraisal to {text_array[initial+1]} has been received and is being processed.\n'
    else:
        response += '1.Apply for new Appraisal.\n2.View current Appraisals.\n'
        
    response += '\n00.Main Menu.\n'
    return response

def loanSchedule(text_array,initial):
    response = 'CON Loans Schedule\n'
    if len(text_array) > initial:
        loan_no = text_array[initial]
        for i in range(1,3):
            response += f'Period {i} \t Payment Date: {datetime.today()}\nOpening Balance {3000},\nPrincipal {350},Interset {120},\nPayment{1500},\nClosing Balance {1620}\n'
            response += '================================\n'
    else:
        response += 'Enter Loan No.\n'
    response += '00.Main Menu\n'
    return response
async def loanDelete(text_array,initial=0,user=None,session_id=None):
    global user_state
    response = 'CON Delete Loan.\n'
    if  user_state[session_id]['user'].get('loans'):
        loans =  user_state[session_id]['user']['loans']
    else:
        loans = await Loans.find(user)
        user_state[session_id]['user']['loans'] = loans
    status = {0:'Deleted',1:"Applied",2:"Guarantors",3:"Endorsements",4:"Disbursed"}
    if len(text_array) > initial:
        loan_no = text_array[initial]
        selected = None
        if len(str(loan_no)) == 1:
            ind = 0            
            for loan in loans:
                if int(loan['Status']) < 4:
                    ind += 1
                    if ind == int(loan_no):
                        selected = loan
                        break
        else:
            for loan in loans:
                if loan['LoanNo'] == loan_no:
                    selected = loan
                    break
        if selected == None:
            response += 'Selected Loan deoes not exist\n#.previous Menu\n00.Main Menu\n'
            return response
        result = await Loans.delete(selected,user)
        if result and result == True:
            response += f'Loan {selected['LoanNo']} has been submitted for deletion. Checkin to view progress.\n'
        else:
            response += "An error occured during submission of request.\nTry again later.\n"
    else:
        ind = 0
        
        for loan in loans:
            if int(loan['Status']) < 4:
                ind += 1
                response += f"{ind}. Loan {loan['LoanNo']} - {float(loan['LoanAmt'])} @ {float(loan['Interest'])}% ({status[int(loan['Status'])]})\n"
        if len(loans) == 0:
            response += "You have no Loans. Proceed to apply\n"
        else:
            response += 'Enter Loan No.\n'
    response += '#.previous Menu\n00.Main Menu\n'
    return response

def receiptPosting(text_array,initial=0):
    response = 'CON Receipt Posting - MPA\n'
    if len(text_array) > initial:
        if len(text_array) - initial == 1:
            receipt_no = text_array[initial]
            response += 'Select Payment Mode.\n'
            response += '1.Cheque\n2.Mpesa\n3.Bank Deposit\n4.Dividends\n5.Mobi Cash\n'
        elif len(text_array) - initial == 2:
            mode = text_array[initial+1]
            if mode == '1':
                mode = 'Cheque'
            elif mode == '2':
                mode = 'Mpesa'
            elif mode == '3':
                mode = 'Bank Deposit'
            elif mode == '4':
                mode = 'Dividends'
            elif mode == '5':
                mode = 'Mobi Cash'
            else:
                response = 'END Invalid Input'
                return response
            if mode == 'Bank Deposit':
                response += 'Enter Bank Name.\n'
            else:
                response += 'Enter Narration.\n'
                
        elif len(text_array) - initial == 3:
            bank = text_array[initial+2]
            response += 'Enter Amount paid.\n'
        else:
            amount = text_array[initial+3]
            response += f'Receipt {text_array[initial]} of amount {text_array[initial+3]} has been added.\n'
    else:
        response += 'Enter Receipt\\Transaction No.\n'
    response += '00.Main Menu\n'
    return response

def myTransactions(text_array):
    response = 'CON My Transactions.\n'

    response += '00.Main Menu.\n'
    return response

def shareTansfers(text_array,initial=0):
    response = 'CON Share Transfers.\nAvailable Shares {1000}'
    if len(text_array) > initial:
        if len(text_array) -initial == 1:
            response += 'Enter Shares to Transfer.\n'
        elif len(text_array) -initial == 2:
            transfer_shares = text_array[initial+1]
            if transfer_shares < 100:
                response += 'Minimum share transfer is {100} shares.\n'
                return response
            response += f'You have transferred {text_array[initial+1]} to Member {text_array[initial]}.\n'
        else:
            response += 'Invalid input.\n'
    else:
        response += 'Enter Receipents Member No.\n'
    response += '00.Main menu.\n'
    return response

def shareLoanOffset(text_array,initial=0):
    response = 'CON Share to Loan Offseting.\n'
    if len(text_array) > initial:
        if len(text_array) -initial == 1:
            response += 'Enter Loan No.\n'
        elif len(text_array) -initial == 2:
            response += f'Loan {text_array[initial+1]} has been offset with {text_array[initial]}.\n'
        else:
            response += 'Invalid input.\n'
        
    else:
        response += 'Enter Offset Amount.\n'
    response += '00.Main menu.\n'
    return response

async def myShares(text_array,initial=0,user=None,session_id=None):
    response = 'CON My Shares.\n'
    if len(text_array) > initial:
        shares = await Shares.my_shares(user)
        print("my shares=>",shares)
        if text_array[initial] == '1':
            response = 'CON Individual Shares.\n'
            index = 0
            total = 0
            for share in shares:
                index += 1
                total += float(share['Amount'])
                response += f'{index}. Amount {float(share['Amount'])} || Code {share['SharesCode']}\n'
            response += f"Total Shares = {total}\n"
        elif text_array[initial] == '2':
            response = 'CON Company Shares.\n'
    else:
        response += '1.Individual Shares.\n\n'
    response += '#.Previous Menu\n00.Main menu.\n'
    return response

async def myLoans(text_array,initial=0,user=None,session_id=None):
    global user_state
    response = 'CON My Loans.\n'
    if len(text_array) > initial:
        if user_state[session_id]['user'].get('loans'):
            loans = user_state[session_id]['user']['loans']
        else:
            loans = await Loans.find(user)
            user_state[session_id]['user']['loans'] = loans
        #print("my loans=>",loans)
        status = {0:'Deleted',1:"Applied",2:"Guarantors",3:"Endorsements",4:"Disbursed"}
        print("len",len(text_array) - initial)
        if len(text_array) - initial > 1:
            loan_no = text_array[-1]
            current_loan = None
            if text_array[initial] == '1':
                ind = 0
                for loan in loans:
                    if int(loan['Status']) != 1:
                        ind += 1
                        if ind == int(loan_no):
                            current_loan = loan
                            break
            if text_array[initial] == '2':
                ind = 0
                for loan in loans:
                    if int(loan['Status']) == 1:
                        ind += 1
                        if ind == int(loan_no):
                            current_loan = loan
                            break
            if text_array[initial] == '3':
                ind = 0
                for loan in loans:
                    if int(loan['Status']) == 0:
                        ind += 1
                        if ind == int(loan_no):
                            current_loan = loan
                            break
            if current_loan == None:
                response = 'CON Invalid loan selected.\n#Previous Menu\n00.Main Menu\nq.exit\n'
                return response
            response = f'CON Viewing Loan {current_loan['LoanNo']}.\n'
            response += f'Applied Amount : {float(current_loan['LoanAmt'])}.\nApplied Date : {current_loan['ApplicDate']}.\n'
            response += f'Interest on Loan : {float(current_loan['Interest'])}%.\nRepayment Period : {int(current_loan['RepayPeriod'])} Months.\n'
            response += f'Loan Status : {int(current_loan['Status'])}.\n'
        else:
            if text_array[initial] == '1':
                response = 'CON Approved Loans.\n'
                ind = 0
                for loan in loans:
                    if int(loan['Status']) != 1:
                        ind += 1
                        response += f"{ind}. Loan {loan['LoanNo']} - {float(loan['LoanAmt'])} @ {float(loan['Interest'])}% ({status[int(loan['Status'])]})\n"
            elif text_array[initial] == '2':
                response = 'CON Pending Loans.\n'
                ind = 0
                for loan in loans:
                    if int(loan['Status']) == 1:
                        ind += 1
                        response += f"{ind}. Loan {loan['LoanNo']} - {float(loan['LoanAmt'])} @ {float(loan['Interest'])}% ({status[int(loan['Status'])]}) \n"
            elif text_array[initial] == '3':
                response = 'CON Deleted Loans.\n'
                ind = 0
                for loan in loans:
                    if int(loan['Status']) == 0:
                        ind += 1
                        response += f"{ind}. Loan {loan['LoanNo']} - {float(loan['LoanAmt'])} @ {float(loan['Interest'])}% ({status[int(loan['Status'])]})\n"
        
    else:
        response += '1.Approved Loans.\n2.Pending Loans.\n3.Deleted Loans.\n'
    response += '#.Previous Menu\n00.Main menu.\n'
    return response

def myMembers(text_array,initial=4):
    response = 'CON Members registered under my company.\n'

    response += '00.Main menu.\n'
    return response

def myMembersShare(text_array,initial=4):
    response = 'CON Members shares under my company.\n'
    if len(text_array) > initial:
        if len(text_array)-initial == 1 and text_array[initial] == '1':
            response += 'Viewing All Share members.\n'
        else:
            if len(text_array)-initial == 1:
                response += 'Enter Member No\\Id No\\Phone No.\n'
            else:
                member = text_array[initial+1]
                response += f'Viewing Shares for member {member}.\n'
    else:
        response += '1.View All.\n2.Search Member.\n'
    response += '00.Main menu.\n'
    return response

async def MemberWithdrawal(text_array,initial=0,user=None,session_id=None):
    response = 'CON Member Withdrawal\n'
    if len(text_array) > initial:
        if len(text_array)-initial == 1 and text_array[initial] == '1':
            response = 'CON Withdrawal Reason \n'
        elif len(text_array)-initial == 2:
            reason = text_array[initial+1]
            result = await Members.withdraw(user)
            if result and result == True:
                response = 'END You have withdrawn your Membership Status.Goodbye\n'
            else:
                response = 'Failed to withdraw membership contact supprt or try again later.\n'
        else:
            response += 'Cancelled\n'

    else:
        response += f'Membership Status : {'Active' if user['memberwithdrawaldate'] == None else 'Withdrawn'}\nDo you wish to proceed?\n1.YES\n2.No\n'
    response+= '#.Previous Menu\n00.Main Menu\n'
    return response
