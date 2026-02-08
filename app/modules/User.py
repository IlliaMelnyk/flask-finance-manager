class User:
    def __init__(self, fullname, username,
                  email, password, uid, 
                  creationDate, balance, budget,
                  account, roles=None, accessRights=None):
        self.fullname=fullname
        self.username=username
        self.email=email
        self.paswword=password
        self.uid=uid
        self.creationDate=creationDate
        self.balance=balance
        self.budget=budget
        self.account=account
        self.roles=roles if roles else [] 
        self.accessRights=accessRights if accessRights else [] 
       

    def get_name(self):
        return self.username

    def get_roles(self):
        return self.roles

    def get_id(self):
        return self.uid

    def get_account(self):
        return self.account
    
    def get_rights(self):
        return self.accessRights

    def add_role(self,role):
        self.roles.append(role)
    
    def remvoe_role(self,role):
        self.roles.remove(role)

    def add_acces_right(self,rigth):
        self.accesRights.append(rigth)
    
    def remove_acces_right(self,right):
        self.accesRights.remove(right)
  
