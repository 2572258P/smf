
from module import cls

def sort():
    ls = [cls(1),cls(2),cls(3)]
    sr = sorted(ls,key = cls.getval,reverse=True)

#Type?
def type():
    c = cls(1)
    print(type(c))
    print(sr[0].val)

def mvh():
    #multi values in hash?
    h = {}
    h['a'] = [0,1]
    h['b'] = [2,3]
    print(h['a'])

mvh()