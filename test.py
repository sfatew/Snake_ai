class q:
    def __init__(self):
        self.a=2
        self.p()

    def p(self):
        self.c=2
        return 3
    
    def i(self):
        self.a = 4
    
    def j(self):
        self.i()


qo=q()
# print(qo.c)
qo.i
print(qo.a)