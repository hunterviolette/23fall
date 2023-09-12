
from sympy import symbols, solve, Eq, nsolve
from scipy.optimize import root

class CH7(object):

  @staticmethod
  def spca(f, p, i, m, n): # returns future
    return solve(Eq(
        f, p * (1 + (i / m))**(n*m)
      ))[0]
  
  @staticmethod
  def sppw(p, i, m, n): # Returns principal
    return p * (1 + (i / m))**(n*m)
  
  @staticmethod
  def apyapr(iEff, iNom, m):
    return solve(Eq(
        iEff, (1 + (iNom / m))**m - 1
      ))[0]

  @staticmethod
  def annuity(p, i, m, n, a, solveFor):
    return solve(Eq(
        a, 
        p * (i / m * (1 + i / m)**(n*m)) / \
            ((1 + i / m)**(n*m) - 1)
      ), solveFor)[0] 
    
  @staticmethod
  def abc(p, i, m, n, a):
    return solve(Eq(
        a, 
        p * (i / m * (1 + i / m)**(n*m)) / \
            ((1 + i / m)**(n*m) - 1)
      ))[0] 
    
  @staticmethod
  def spca_scipy(f, p, i, m, n): # returns future
    def eqn(i, f, p, m, n):
        return p * (1 + (i / m))**(n * m) - f
        
    return root(eqn, x0=0).x[0]
  
  @staticmethod
  def annuity_scipy(p, i, m, n, a): # returns future
    def eqn(p, i, m, n, a):
        return p * (i / m * (1 + i / m)**(n*m)) / \
            ((1 + i / m)**(n*m) - 1) - a
        
    return root(eqn, x0=0).x[0]
    
class CHE477(CH7):
  pass


