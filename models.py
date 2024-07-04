
class Member:
    #def __init__(self,id,MemberNo,StaffNo,IDNo,Surname,OtherNames,Sex,DOB,Employer,Dept,Rank,Terms,PresentAddr,OfficeTelNo,HomeAddr,HomeTelNo,RegFee,InitShares,AsAtDate,MonthlyContr,ApplicDate,EffectDate,Signed,Accepted,Archived,Withdrawn,Province,District,Station,CompanyCode,CIGCode,PIN,Photo,ShareCap,BankCode,Bname,AuditID,AuditTime,E_DATE,posted,initsharesTransfered,Transferdate,LoanBalance,InterestBalance,FormFilled,EmailAddress,accno,memberwitrawaldate,Dormant,MemberDescription,email,TransactionNo,MobileNo,AgentId,PhoneNo,Entrance,status,mstatus,Age,ApiKey,UserName,Run):
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        #return self.get()
    def get(self):
        return self.__dict__

class Company:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        #return self.get()

    def get(self):
        return self.__dict__

class Share:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        #return self.get()
    def get(self):
        return self.__dict__

class Beneficiary:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def get(self):
        return self.__dict__

class Contribution:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def get(self):
        return self.__dict__

class LoanBal:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def get(self):
        return self.__dict__


class LoanType:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def get(self):
        return self.__dict__


class Loan:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def get(self):
        return self.__dict__

class Agent:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def get(self):
        return self.__dict__

class Guarantor:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    def get(self):
        return self.__dict__