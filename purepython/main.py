
class cls():
    def __init__(self,val):
        self.val = val
    def getval(self):
        return self.val

ls = [cls(1),cls(2),cls(3)]
sr = sorted(ls,key = cls.getval,reverse=True)

print(sr[0].val)