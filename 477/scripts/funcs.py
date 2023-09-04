
from sympy import symbols, solve, Eq

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
  def annuity(p, i, m, n, a):
    return solve(Eq(
        a, 
        p * ((i / m) * (1 + (i / m))**(n*m)) / \
        ((1 + (i /m))**(n*m) - 1)
      ))[0] 

class CHE477(CH7):
  pass


