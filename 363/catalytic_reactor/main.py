import sympy as sp
import pandas as pd
import pint

uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"
q = uReg.Quantity

class UncertCalc:
  def __init__(self) -> None:
    pass

  @staticmethod
  def Print(metric, f, comps, sub):
    print('======',
          f'{metric} Uncert',
          f'Function: {f}',
          UncertCalc.Uncert(f, comps, sub),
          sep='\n')
    
  @staticmethod
  def ListMean(x: list):
    return (sum(x) / len(x)).__round__(2)

  def MeanFlowRate(self):
    coarse = [[5, 28.25], [5, 27.61], [5.2, 26.8]]
    fine = [[5, 27.38], [5.1, 28.91], [5, 27.4]]
    
    coarseFlows = []
    for c in coarse:
      coarseFlows.append(q(c[0] / c[1], 'mL/s').to('mL/min'))

    fineFlows = []
    for f in fine:
      fineFlows.append(q(c[0] / c[1], 'mL/s').to('mL/min'))

    self.coarseFlow = UncertCalc.ListMean(coarseFlows)
    self.fineFlow = UncertCalc.ListMean(fineFlows)

  @staticmethod
  def Flow():
    v, t = sp.symbols('v t')
    f = v / t

    v_, t_ = 5, 28.25
    vu, tu = v_ * .01, t_ * .01

    sub = {v: v_, t: t_}
    comps = [[v, vu], [t, tu]]

    UncertCalc.Print('Flow Rate', f, comps ,sub)

  def ResidenceTime(self):
    UncertCalc.MeanFlowRate(self)

    h, d, Q = sp.symbols('h d Q')
    f = sp.pi * h * (d / 2)**2 / Q

    Q_ = self.coarseFlow.magnitude
    h_ = q(23.4, 'cm').to('mm').magnitude
    d_ = 25

    Qu, hu, du = Q_*.01, h_*.01, d_*.01
    
    sub = {h: h_, d: d_, Q: Q_}
    comps = [[h, hu], [d, du], [Q, Qu]]

    UncertCalc.Print('Residence Time', f, comps, sub)

  @staticmethod
  def RateConstants():
    xC, tau = sp.symbols('xC tau')
    f = -sp.ln(1 - xC) / tau

    xC_, tau_ = .2, 10.402
    xCu, tauu  = xC_ *.01, tau_ *.01

    sub = {xC: xC_, tau: tau_}
    comps = [[xC, xCu], [tau, tauu]]

    UncertCalc.Print('Rate Constant', f, comps, sub)

  @staticmethod
  def ThieleModulus():
    phiC, rC, rF, kC, kF = sp.symbols('phiC rC rF kC kF')
    f = (1 / sp.tanh(phiC) - 1 / phiC) / \
        (1 / sp.tanh(phiC * rF / rC) - (1 / (phiC * rF / rC))) - \
        ((kC * rC) / (kF * rF))
  
    phiC_ = -2.565
    rC_, rF_ = .88 / 2, .31 /2
    kC_, kF_ = 3.575e-4, 4.666e-4

    phiCu = phiC_ *.01
    rCu, rFu = rC_ *.01, rF_ *.01
    kCu, kFu = kC_ *.01, kF_ *.01 

    sub = {phiC: phiC_, rC: rC_, rF: rF_, kC: kC_, kF: kF_}
    comps = [[phiC, phiCu], [rC, rCu], [rF, rFu], [kC, kCu], [kF, kFu]]
    
    UncertCalc.Print('Thiele Modulus', f, comps, sub)

  def EffectivenessFactor(self):
    phiC = sp.symbols('phiC')
    f = 3 / phiC * (1 / sp.tanh(phiC) - 1/phiC)

    phiC_ = -2.565
    phiCu = phiC_ * .01

    sub = {phiC: phiC_}
    comps = [[phiC, phiCu]]

    UncertCalc.Print('Effectiveness Factor', f, comps, sub)

  def TrueRateConstants(self):
    kC, etaC = sp.symbols('kC etaC')
    f = kC / etaC

    kC_, etaC_ = 3.575e-4, .6
    kCu, etaCu = kC_ *.01, etaC_ *.01

    sub = {kC: kC_, etaC: etaC_}
    comps = [[kC, kCu], [etaC, etaCu]]

    UncertCalc.Print('True Rate Constants', f, comps, sub)

  def Diffusivity(self):
    kTC, phiC, rC = sp.symbols('kTC phiC rC')
    f = kTC / (phiC / rC)**2

    kTC_, phiC_, rC_ = 1, -2.565, .88 / 2
    kTCu, phiCu, rCu = kTC_ *.01, phiC_ *.01, rC_ *.01

    sub = {kTC: kTC_, phiC: phiC_, rC: rC_}
    comps = [[kTC, kTCu], [phiC, phiCu], [rC, rCu]]

    UncertCalc.Print('Diffusivity', f, comps, sub)

  @staticmethod
  def Uncert(f, # Function 
            comps: list, # List of variables in function 
            sub: dict # Subsitution of variables with numbers
          ):

    df = pd.DataFrame()
    for comp in comps:
        assert len(comp) == 2
        
        df = pd.concat([
            df,
            pd.DataFrame({
              'Component': [comp[0]],
              'Value': [sub[comp[0]]],
              'Uncert Value': [comp[1]],
              'Relative Uncert': [(sp.diff(f, comp[0]).subs(sub)**2 * comp[1]**2)**.5],
            })
        ])

    df = df.astype({"Relative Uncert": 'float'})

    df["Total Uncert"] = df["Relative Uncert"].sum()
    df['Uncert Contribution'] = df["Relative Uncert"] / df["Total Uncert"]

    return df.set_index('Component').round(4)
  
  def All(self):
    UncertCalc.Flow()
    UncertCalc.ResidenceTime(self)
    UncertCalc.RateConstants()
    UncertCalc.ThieleModulus()
    UncertCalc.EffectivenessFactor(self)
    UncertCalc.TrueRateConstants(self)
    UncertCalc.Diffusivity(self)


UncertCalc().All()