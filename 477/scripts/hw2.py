from funcs import CHE477
from scipy.optimize import root

class HW2(CHE477):
    
    @staticmethod
    def One():
        print('==== Problem 1 ====')

        f = (15 + 20 + 22 + 21 + 26 + 26)*10000
                
        def eqn(i, f=f, p=10**6, m=12, n=6):
            return p * (1 + (i / m))**(n * m) - f
            
        sol = root(eqn, x0=0)
        print(f"Interest rate (%): {sol.x[0]*100}")
        
    @staticmethod
    def Two():
        print('==== Problem 2 ====')

    @staticmethod
    def Three():
        print('==== Problem 3 ====')
        
        m2, m1, i = 12, 365, .05 
        i2 = m2 * ((1 + i / m1)**(m1 / m2) - 1)
        
        def eqn(a, p=40000, i=i2, m=12, n=5):
            return p * (i / m * (1 + i / m)**(n*m)) / ((1 + i / m)**(n*m) - 1) - a
            
        sol = root(eqn, x0=500)
        print(f"Monthly Payment: {sol.x[0]}")
        

    @staticmethod
    def Four():
        print('==== Problem 4 ====')

        gi, g, i, n, m = 80, 65, .04, 15, 1
        
        a_ = g * ((1 / i / m) - n / ((1 + i/ m)**(n*m) - 1))
        print(a_)
    
    @staticmethod
    def Five():
        print('==== Problem 5 ====')
        
        c2012, c2022 = 585, 816
        x = (c2022 / c2012)**(1/20) - 1
        print(f"Avg Inflation rate (%): {x*100}")
        
    
    @staticmethod
    def All():
        HW2.One()
        HW2.Three()
        HW2.Four()
        HW2.Five()
    
        
HW2.Five()