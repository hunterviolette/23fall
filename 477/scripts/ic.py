from funcs import CHE477
from sympy import symbols, nsolve, Eq

import pandas as pd

p = 250000
x_ = symbols('x')
a = CHE477.annuity(p, .03625, 12, 30, x_, x_)
total = a*12*30

interestPaid = total - p

#df = pd.DataFrame()
#for x in range(1,)

print(interestPaid)

x = symbols('x')
p, i, m = 250000, 0.03625, 12
a = (a + 1000).__round__(2)
print(a)

eqn = a - p * (i / m * (1 + i / m)**(x*m)) / ((1 + i / m)**(x*m) - 1)
v = nsolve(eqn, x)
print(v)