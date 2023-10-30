import sympy as sp
import pandas as pd

from math import pi

class UncertCalc:
  def __init__(self, trial: str = '1_coarse') -> None:

    df = pd.read_csv('dat.csv', index_col='trial')
    self.s = df.loc[df.index == trial].squeeze()

    self.df = pd.DataFrame()
    
    print(f'=== Input data, trial: {trial} ===',
          self.s, '========', sep='\n')

  def Uncert(self,
            metric: str, # Function name
            f: sp.core.mul.Mul, # Function 
            comps: list, # List of lists of [var, var_uncert]
            sub: dict # Subsitution of variables with values
          ):

    df = pd.DataFrame()
    for comp in comps:
        assert len(comp) == 2
        
        df = pd.concat([
            df,
            pd.DataFrame({
              'Variable': [comp[0]],
              'Input Value': [sub[comp[0]]],
              'Input Uncert Value': [comp[1]],
              'Component Uncert': [(sp.diff(f, comp[0]).subs(sub)**2 * comp[1]**2)**.5],
            })
        ])

    df = df.astype({"Component Uncert": 'float'})

    df["Total Uncert"] = df["Component Uncert"].sum()
    df["Relative Uncert (%)"] = ((df["Total Uncert"] / f.subs(sub))*100).astype('float')
    df['Uncert Contribution (%)'] = (df["Component Uncert"] / df["Total Uncert"])*100 -1 
    
    df = df.round({
        "Uncert Contribution (%)": 2,
        "Relative Uncert (%)": 2,
      })
    
    df["Metric"] = metric

    print(f"{metric}: {f}")
    self.df = pd.concat([self.df, df.set_index(['Metric', 'Variable'])])
    
  def Flow(self):
    v, t = sp.symbols('v t')
    f = v / t

    v_ = self.s["volume_flow (mL)"]
    t_ = self.s["time_flow (sec)"]

    sub = {v: v_, t: t_}
    comps = [[v, v_ * .01], [t, t_ * .01]]

    UncertCalc.Uncert(self, 'Flow Rate', f, comps, sub)

  def ResidenceTime(self):
    h, d, q = sp.symbols('h d q')
    f = pi * h * (d / 2)**2 / q

    q_ = self.s["flow_rate (mL/min)"]
    h_ = self.s["height_col (mm)"]
    d_ = self.s["diam_col (mm)"]
    
    sub = {h: h_, d: d_, q: q_}
    comps = [[h, h_*.01], [d, d_*.01], [q, q_*.01]]

    UncertCalc.Uncert(self, 'Residence Time', f, comps, sub)

  def RateConstants(self):
    xC, tau = sp.symbols('xC tau')
    f = -sp.ln(1 - xC) / tau

    xC_ = self.s["x_convers"]
    tau_ = self.s["tau_c (min)"]

    sub = {xC: xC_, tau: tau_}
    comps = [[xC, xC_ *.01], [tau, tau_ *.01]]

    UncertCalc.Uncert(self, 'Rate Constant', f, comps, sub)

  def ThieleModulus(self):
    phiC, rC, rF, kC, kF = sp.symbols('phiC rC rF kC kF')
    f = (1 / sp.tanh(phiC) - 1 / phiC) / \
        (1 / sp.tanh(phiC * rF / rC) - (1 / (phiC * rF / rC))) - \
        ((kC * rC) / (kF * rF))
      
    phiC_ = self.s["phi_c"]
    rC_ = self.s["radius_c_particle (mm)"] / 2
    rF_ = self.s["radius_f_particle (mm)"] / 2
    kC_ = self.s["k_c (1/s)"]
    kF_ = self.s["k_f (1/s)"]

    sub = {phiC: phiC_, rC: rC_, rF: rF_, kC: kC_, kF: kF_}
    comps = [[phiC, phiC_ *.01], [rC, rC_ *.01], 
             [rF, rF_ *.01], [kC, kC_ *.01], [kF, kF_ *.01]]
    
    UncertCalc.Uncert(self, 'Thiele Modulus', f, comps, sub)

  def EffectivenessFactor(self):
    phiC = sp.symbols('phiC')
    f = 3 / phiC * (1 / sp.tanh(phiC) - 1/phiC)

    phiC_ = self.s["phi_c"]

    sub = {phiC: phiC_}
    comps = [[phiC, phiC_ * .01]]

    UncertCalc.Uncert(self, 'Effectiveness Factor', f, comps, sub)

  def TrueRateConstants(self):
    kC, etaC = sp.symbols('kC etaC')
    f = kC / etaC

    kC_ = self.s["k_c (1/s)"]
    etaC_ = self.s["eta_c"]

    sub = {kC: kC_, etaC: etaC_}
    comps = [[kC, kC_ *.01], [etaC, etaC_ *.01]]

    UncertCalc.Uncert(self, 'True Rate Constants', f, comps, sub)

  def Diffusivity(self):
    kTC, phiC, rC = sp.symbols('kTC phiC rC')
    f = kTC / (phiC / rC)**2

    kTC_ = self.s["kT_c (1/s)"]
    phiC_ = self.s["phi_c"]
    rC_ = self.s["radius_c_particle (mm)"] / 2

    sub = {kTC: kTC_, phiC: phiC_, rC: rC_}
    comps = [[kTC, kTC_ *.01], [phiC, phiC_ *.01], [rC, rC_ *.01]]

    UncertCalc.Uncert(self, 'Diffusivity', f, comps, sub)
  
  def All(self):
    UncertCalc.Flow(self)
    UncertCalc.ResidenceTime(self)
    UncertCalc.RateConstants(self)
    UncertCalc.ThieleModulus(self)
    UncertCalc.EffectivenessFactor(self)
    UncertCalc.TrueRateConstants(self)
    UncertCalc.Diffusivity(self)

    print('========', self.df, sep='\n')

UncertCalc().All()