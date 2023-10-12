import random

def small():
    U = 0 + random.randint(0, 30000)//1000*1000
    return U
    
def average():
    U = 30000 + random.randint(30000, 200000)//1000*1000
    return U

def high():
    U = 200000 + random.randint(200000, 1000000)//1000*1000
    return U

def critical():
    U = 1000000 + random.randint(1000000, 5000000)//1000*1000
    return U

def super():
    U = 5000000 + random.randint(5000000, 7000000)//1000*1000
    return U

t = '12'

while t!='11':
    t = input()
    if t == '0':
        print(small())

    elif t == '1':
        print(average())

    elif t == '2':
        print(high())

    elif t == '3':
        print(critical())

    elif t == '4':
        print(super())

    elif t == '':
        pass

    else:
        pass
