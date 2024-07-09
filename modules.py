from db import DatabaseManager
from models import *
from modules import *

class Companies:
    @staticmethod
    async def find(code):
        company = await DatabaseManager.query(f"select * from COMPANY where CompanyCode='%s'"%(code))
        if company and len(company) > 0:
            company = company[0]
            company = Company(
                id = company[0],
                CompanyCode = company[1],
                CompanyName = company[2],CIGCode = company[3],
                CountyCode = company[4],County=company[5],
                email = company[10],
                Contactperson=company[11],
                Telephone = company[12],Address=company[13],AccountNo=company[14],
                NoYears=company[15],NoEmployees = company[16],Location=company[17],
                type=company[18],Capital=company[21]
            )
            company = company.get()
            
        else:
            company = None
        return company

class Agents:
    @staticmethod
    async def find(id):
        agent = await DatabaseManager.query(f"select * from Agents where id='%s' or IdNo='%s'"%(id,id))
        if agent == None or len(agent) == 0:
            return None
        agent = agent[0]
        agent = Agent(
            id = agent[0],
            Names = agent[1],Gender = agent[2],
            staffcode = agent[3],IdNo = agent[4],
            Occupation = agent[5],LandPhone = agent[6],
            MobileNo = agent[6],branchName = agent[7],
            CompanyCode = agent[8],HomeAddress = agent[9],
            Town = agent[10]
        )
        return agent.get()
class Contrib:
    @staticmethod
    async def find(member_no):
        return {
            'member_no':member_no
        }

class Shares:
    @staticmethod
    async def my_shares(user):
        contribs = await DatabaseManager.query(f"select * from CONTRIB where MemberNo='%s' and CompanyCode='%s'"%(user['MemberNo'],user['CompanyCode']))
        if contribs == None or len(contribs) == 0:
            return []
        contributions = []
        for contrib in contribs:
            c = Contribution(id=contrib[0],MemberNo=contrib[1],Amount=contrib[7],ShareBal=contrib[8],
                CompanyCode = contrib[10],SharesCode = contrib[30])
            contributions.append(c.get())

        return contributions

    @staticmethod
    async def find(code):
        shares = await DatabaseManager.query(f"select * from sharetype where CompanyCode='%s'"%(code))
        if shares and len(shares) > 0:
            shares = shares[0]
            shares = Share(
                SharesCode = shares[0],
                SharesType = shares[1],LoanToShareRatio = shares[4],
                Issharescapital = shares[5],Interest = shares[6],
                CompanyCode = shares[7],MaxAmount = shares[8],
                MinAmount = shares[-4]
            )
            shares = shares.get()
        else:
            shares = None
        return shares

class Loans:
    @staticmethod
    async def delete(loan,user):
        result = DatabaseManager.update(f"update LOANS set status=0 where MemberNo='%s' and CompanyCode='%s' and LoanNo='%s'"%(user['MemberNo'],user['CompanyCode'],loan['LoanNo']))
        if result and result == True:
            return True
        return None
    @staticmethod
    async def find(user):
        result = await DatabaseManager.query(f"select * from LOANS where MemberNo='%s' and CompanyCode='%s' "%(user['MemberNo'],user['CompanyCode']))
        if result == None or len(result) == 0:
            return []
        loans = []
        for loan in result:
            l = LoanBal(id=loan[0],LoanNo=loan[1],
                MemberNo = loan[2],LoanCode = loan[3],
                ApplicDate=loan[4],LoanAmt=loan[5],
                RepayPeriod = loan[6],CompanyCode=loan[10],
                IdNo=loan[11],Interest=loan[36],
                Status=loan[38]
            )
            loans.append(l.get())
        return loans
    @staticmethod
    async def get_types(company):
        query = await DatabaseManager.query(f"select * from LOANTYPE where CompanyCode='%s'"%(company))
        if query == None or len(query) == 0:
            return []
        types = []
        for loan in query:
            l = LoanType(LoanCode=loan[0],
                LoanType=loan[1],CompanyCode=loan[2],
                RepayPeriod = loan[11],
                Interest = loan[12],
                MaxAmount = loan[13],
                MaxLoans =loan[30],
                RepayMethod = loan[31],ID = loan[37]
            )
            types.append(l.get())
        return types
    @staticmethod
    async def get_next(user,Type):
        query = await DatabaseManager.query(f"select id,LoanNo from LOANS where CompanyCode='%s' and LoanCode='%s' order by id desc"%(user['CompanyCode'],Type['LoanCode']))
        if query == None or len(query) == 0:
            query_n = await DatabaseManager.query(f"select id from LOANS order by id desc")
            if query_n == None or len(query_n) == 0:
                n_id = 1
            else:
                n_id = int(query_n[0][0])+1
            loan_no = Type['LoanCode']+user['MemberNo']
            return {'LoanNo':loan_no,'id': n_id}
        query = query[0]
        if "-" in  str(query[1]):
            loan_no = str(query[1]).split("-")[-1]
            loan_no = int(loan_no)+1
            loan_no = Type['LoanCode']+user['MemberNo']+"-"+str(loan_no)
        else:
            loan_no = query[1]+"-1"
        return {'LoanNo':loan_no,'id': int(query[0])+1}
    @staticmethod
    async def add(loan):
        query = await DatabaseManager.query(f"select * from LOANS where LoanNo='%s' and CompanyCode='%s'"%(loan['LoanCode'],loan['CompanyCode']))
        if query != None and len(query) != 0:
            return True
        new = DatabaseManager.insert(f"insert into LOANS (LoanNo,MemberNo,LoanCode,LoanAmt,RepayPeriod,CompanyCode,IdNo,Interest,Status,ApplicDate) values('%s','%s','%s','%s','%s','%s','%s','%s','%s',current_timestamp)"%(loan['LoanNo'],loan['MemberNo'],loan['LoanCode'],loan['LoanAmt'],loan['RepayPeriod'],loan['CompanyCode'],loan['IdNo'],loan['Interest'],loan['Status']))
        if new and new == True:
            return True
        return None

class Guarantors:
    @staticmethod
    async def find(user):
        query = await DatabaseManager.query(f"select * from  where LoanNo like '%s' and ComapnyCode='%s' or LoanNo like '%s' and CompanyCode is NULL"%("%"+user['MemberNo']+"%",user['CompanyCode'],"%"+user['MemberNo']+"%"))
        if query == None or len(query) == 0:
            return []
        guarantors = []
        for r in query:
            g = Guarantor(
                MemberNo = r[0],LoanNo=r[1],Amount=r[2],Balance=r[3],FullNames=r[10],CompanyCode=r[12]
            )
            guarantors.append(g.get())
        return guarantors
class Beneficiaries:
    @staticmethod
    async def get_last(member):
        result = await DatabaseManager.query(f"select KinNo from KIN where MemberNo='%s' order by SignDate DESC"%(member))
        if result == None or len(result) == 0:
            return f'K{member}-1'
        num = result[0]
        next = num.split("-")[-1]+1
        return f'K{member}-{next}'
    @staticmethod
    async def add(kin):
        result = DatabaseManager.insert(f"insert into KIN (MemberNo,KinNames,KinNo,Address,IDNo,Relationship,CompanyCode,HomeTelNo,Percentage,Comments,AuditID) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(kin['MemberNo'],kin['KinNames'],kin['KinNo'],kin['Address'],kin['IDNo'],kin['Relationship'],kin['CompanyCode'],kin['Phone'],kin['Percentage'],kin['Comments'],'user'))
        print("result=>",result)
        if result and result == True:
            return True
        return None
    @staticmethod
    async def find(user):
        beneficiaries = []
        result = await DatabaseManager.query(f"select * from KIN where MemberNo like '%s' or KinNo like '%s'"%("%"+user['MemberNo']+"%","%"+user['MemberNo']+"%"))
        if result == None or len(result) == 0:
            beneficiaries = []
        for r in result:
            bn = Beneficiary(MemberNo=r[0],KinNames=r[1],KinNo=r[2],Address=r[3],
                IDNo = r[4],RelationShip=r[5],HomeTelNo=r[6],CompanyCode=r[7],
                CIGCode=r[8],Witness = r[9],Percentage=r[10],OfficeTelNo=r[11],
                Comments = r[-1]
            )
            beneficiaries.append(bn.get())
        return beneficiaries
class Members:
    @staticmethod
    async def get_last(company,county):
        query = await DatabaseManager.query(f"select MemberNo,Employer from Members where CompanyCode='%s' order by id desc"%(company))
        if query == None or len(query) == 0:
            new_query = await DatabaseManager.query(f"select LocationCode from Locations where LocationName like '%s'"%("%"+county+"%"))
            if new_query == None or len(new_query) == 0:
                return {'MemberNo':None,'Employer':None}
            new_query = new_query[0]
            employer = await DatabaseManager.query(f"select CompanyName from Company where CompanyCode='%s'"%(company))
            if employer == None or len(employer) == 0:
                return {'MemberNo':new_query[0]+"000001",'Employer':None}
            employer = employer[0]
            return {'MemberNo':new_query[0]+"000001",'Employer':employer}
        result = query[0]
        new_query = await DatabaseManager.query(f"select LocationCode from Locations where LocationName like '%s'"%("%"+county+"%"))
        if new_query == None or len(new_query) == 0:
            county_code = result[0][:3]
        else:
            county_code = new_query[0][0]
        return {'MemberNo':county_code+str(int(result[0][3:])+1),'Employer':result[1]}
    @staticmethod
    async def create(member):
        result = DatabaseManager.insert(f"insert into MEMBERS (MemberNo,StaffNo,IDNo,Surname,OtherNames,Sex,DOB,Employer,Province,District,Station,CompanyCode,MobileNo,PhoneNo,Age,AgentId) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(member['MemberNo'],member['StaffNo'],member['IDNo'],member['Surname'],member['OtherNames'],member['Sex'],member['DOB'],member['Employer'],member['Province'],member['District'],member['Station'],member['CompanyCode'],member['MobileNo'],member['PhoneNo'],member['Age'],member['AgentId']))
        if result and result == True:
            return True

        return None
    @staticmethod
    async def loanBal(user):
        loanbal = await DatabaseManager.query(f"select * from LOANBAL where MemberNo='%s' and CompanyCode='%s' and Balance > 0"%(user['MemberNo'],user['CompanyCode']))
        if loanbal == None or len(loanbal) == 0:
            return None
        balances = []
        for loan in loanbal:
            bal = LoanBal(id=loan[0],LoanNo=loan[1],
                LoanCode = loan[2],
                MemberNo = loan[3],Balance = loan[4],
                IntrOwed = loan[5],Installments = loan[6],
                FirstDate = loan[8],RepayRate =loan[9],
                LastDate = loan[10],duedate = loan[11],
                intrCharged = loan[12],Interest = loan[13],
                CompanyCode = loan[14],Penalty = loan[15],
                RepayRate2 = loan[16],RepayMethod=loan[17],
                Cleared = loan[18],RepayPeriod = loan[21],
                Remarks = loan[22],Defaulter = loan[28],
                nextduedate = loan[32],TransactionNo=loan[33],
                Year = loan[35],Month = loan[36],
                RepayMode = loan[37]
            )
            balances.append(bal.get())
        sum = 0
        for bl in balances:
            sum+= bl['Balance']
        return {'balances':balances,'loanBal':sum}

    @staticmethod
    async def loan(user):
        contribs = await DatabaseManager.query(f"select * from CONTRIB where MemberNo='%s' and CompanyCode='%s'"%(user['MemberNo'],user['CompanyCode']))
        if contribs == None or len(contribs) == 0:
            return None
        contributions = []
        for contrib in contribs:
            c = Contribution(id=contrib[0],MemberNo=contrib[1],Amount=contrib[7],ShareBal=contrib[8],
                CompanyCode = contrib[10],SharesCode = contrib[30])
            contributions.append(c.get())
        sum_contrib = 0
        share_contrib = 0
        for c in contributions:
            sum_contrib += c['Amount']
            share_contrib += c['ShareBal']
        
        share = None
        if contributions[0].get('SharesCode'):
            shares = await DatabaseManager.query(f"select * from sharetype where CompanyCode='%s' and SharesCode='%s'"%(contributions[0]['CompanyCode'],contributions[0]['SharesCode']))
            if shares == None or len(shares) == 0:
                share = None
            else:
                share = shares[0]
                share = Share(SharesCode=share[0],SharesType=share[1],
                    SharesAcc = share[2],
                    LoanToShareRatio = share[4],
                    CompanyCode = share[7],
                    MaxAmount = share[8],
                    MinAmount = share[-4]
                )
                share = share.get()
        return {'contrib':{'Amount':sum_contrib,'Shares':share_contrib},'share':share}
    @staticmethod
    async def update(user):
        update = DatabaseManager.update(f"update MEMBERS set PIN='%s' where id='%s'"%(user['PIN'],user['id']))
        print("update=>",update)
        if update and update == True:
            return True
        return None
    @staticmethod
    async def login(id):
        company_code = 1234
        share_code = 'SHARE1'
        member_no = 'Member_1'
        member = await DatabaseManager.query(f"select m.*,c.CompanyName FROM [BOSA].[dbo].[MEMBERS] m INNER JOIN Company c ON c.CompanyCode = m.CompanyCode where m.id='%s' or m.IDNo='%s'"%(id,id))
        if member == None or len(member) == 0:
            return None
        member = member[0]
        result = Member(id=member[0],MemberNo=member[1],staffNo=member[2],
            IDNo = member[3],Surname = member[4], OtherNames = member[5],
            Sex = member[6],
            DOB = member[7],Employer = member[8],
            Dept = member[9], Rank = member[10],
            Terms = member[11],PresentAddr = member[12],
            OfficeTelNo = member[13], HomeAddr = member[14],
            HomeTelNo = member[15], RegFee = member[16],
            InitShares = member[17], AsAtDate = member[18],
            MonthlyContr = member[19],ApplicDate = member[20],
            EffectDate = member[21], Signed = member[22],
            CompanyCode = member[29], CIGCode = member[30],
            PIN = member[31],ShareCap = member[33],
            BankCode = member[34], initsharesTransfered = member[40],
            LoanBalance = member[42], InterestBalance = member[43],EmailAddress = member[45],accno=member[46],
            memberwithdrawaldate = member[-16],
            Dormant = member[-15],email = member[-13],
            TransactionNo = member[-12],MobileNo = member[-11],
            AgentId = member[-10],PhoneNo = member[-9],Entrance = member[-8],
            status = member[-7],mstatus = member[-6],Age=member[-5],
            UserName=member[-3],CompanyName=member[-1]
        )
        result = result.get()
        #print("member=>",result)
         
        
        #print("member=>",result)
        return result
        #company = Company.find(company_code)
        #shares = Shares.find(share_code)
        #contributions = Contrib.find(member_no)
    @staticmethod
    async def withdraw(user):
        query =  DatabaseManager.update(f"update MEMBERS set memberwitrawaldate = current_timestamp where MemberNo='%s' and id='%s' "%(user['MemberNo'],user['id']))
        if query and query == True:
            return True
        return None