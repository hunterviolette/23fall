import sympy as sp
import pandas as pd

pd.set_option('display.max_rows', None)

from math import pi

class UncertCalc:
  def __init__(self) -> None:

    self.data = pd.read_csv('dat.csv', index_col='trial')
    self.df = pd.DataFrame()

    self.functions = {}

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
            }).astype({"Component Uncert": 'float'})
        ])

    df["Total Uncert"] = df["Component Uncert"].sum()
    df['Uncert Contribution (%)'] = (df["Component Uncert"] / df["Total Uncert"])*100 
    df["Relative Uncert (%)"] = ((df["Total Uncert"] / f.subs(sub))*100).astype('float')

    if metric == 'Thiele Modulus':
      df["Relative Uncert (%)"] = df["Relative Uncert (%)"].abs() / 1e3
    
    df = df.round({
        "Uncert Contribution (%)": 2,
        "Relative Uncert (%)": 2,
      })
    
    df["Metric"] = metric
    df["Trial"] = self.s["trial"]

    self.df = pd.concat([self.df, df])
    
  def Flow(self):
    v, t = sp.symbols('v t')
    f = v / t

    self.functions["Flow Rate"] = f

    v_ = self.s["volume_flow (mL)"]
    t_ = self.s["time_flow (sec)"]

    sub = {v: v_, t: t_}
    comps = [[v, v_ * .01], [t, t_ * .01]]

    UncertCalc.Uncert(self, 'Flow Rate', f, comps, sub)

  def ResidenceTime(self):
    h, d, q = sp.symbols('h d q')
    f = pi * h * (d / 2)**2 / q
    
    self.functions["Residence Time"] = f

    q_ = self.s["flow_rate (mL/min)"] # 9.47 mL
    h_ = self.s["height_col (mm)"] # 234 mm
    d_ = self.s["diam_col (mm)"] # 25 mm
    
    sub = {h: h_, d: d_, q: q_}
    comps = [[h, h_*.01], [d, d_*.01], [q, q_*.01]]

    UncertCalc.Uncert(self, 'Residence Time', f, comps, sub)

  def RateConstants(self):
    x, tau = sp.symbols('x tau')
    f = -sp.ln(1 - x) / tau

    self.functions["Rate Constant"] = f

    x_ = self.s["frac_conv"]
    tau_ = self.s["tau (min)"]

    sub = {x: x_, tau: tau_}
    comps = [[x, x_ *.01], [tau, tau_ *.01]]

    UncertCalc.Uncert(self, 'Rate Constant', f, comps, sub)

  def ThieleModulus(self):
    phi, rC, rF, kC, kF = sp.symbols('phi rC rF kC kF')
    f = (1 / sp.tanh(phi) - 1 / phi) / \
        (1 / sp.tanh(phi * rF / rC) - (1 / (phi * rF / rC))) - \
        ((kC * rC) / (kF * rF))
    
    self.functions["Thiele Modulus"] = f
      
    phi_ = self.s["phi"]
    rC_ = self.s["radius_c_particle (mm)"] / 2
    rF_ = self.s["radius_f_particle (mm)"] / 2
    kC_ = self.s["k_x (1/s)"]
    kF_ = self.s["k_y (1/s)"]

    sub = {phi: phi_, rC: rC_, rF: rF_, kC: kC_, kF: kF_}
    comps = [[phi, phi_ *.01], [rC, rC_ *.01], 
             [rF, rF_ *.01], [kC, kC_ *.01], [kF, kF_ *.01]]
    
    UncertCalc.Uncert(self, 'Thiele Modulus', f, comps, sub)

  def EffectivenessFactor(self):
    phi = sp.symbols('phi')
    f = 3 / phi * (1 / sp.tanh(phi) - 1/phi)

    self.functions["Effectiveness Factor"] = f

    phi_ = self.s["phi"]

    sub = {phi: phi_}
    comps = [[phi, phi_ * .01]]

    UncertCalc.Uncert(self, 'Effectiveness Factor', f, comps, sub)

  def TrueRateConstants(self):
    k, eta = sp.symbols('k eta')
    f = k / eta

    self.functions["True Rate Constants"] = f

    k_ = self.s["k_x (1/s)"]
    eta_ = self.s["eta"]

    sub = {k: k_, eta: eta_}
    comps = [[k, k_ *.01], [eta, eta_ *.01]]

    UncertCalc.Uncert(self, 'True Rate Constants', f, comps, sub)

  def Diffusivity(self):
    kT, phi, r = sp.symbols('kT phi r')
    f = kT / (phi / r)**2

    self.functions["Diffusivity"] = f

    kT_ = self.s["kT (1/s)"]
    phi_ = self.s["phi"]

    sub = {kT: kT_, phi: phi_, r: self.r}
    comps = [[kT, kT_ *.01], [phi, phi_ *.01], [r, self.r *.01]]

    UncertCalc.Uncert(self, 'Diffusivity', f, comps, sub)

  def Concentration(self):
    slp, a = sp.symbols('slp a')
    f = slp / a

    self.functions["Concentration"] = f

    slp_ = self.s["slp"]
    a_ = self.s["a"]

    sub = {slp: slp_, a: a_}
    comps = [[slp, slp_ *.01], [a, a_ *.01]]

    UncertCalc.Uncert(self, 'Concentration', f, comps, sub)
  
  def All(self):
    for i, x in self.data.iterrows():
      self.s, col = x, i.split("_")[1]
      self.s["trial"] = i
      
      if col == 'coarse': 
        self.r = x['radius_c_particle (mm)'] / 2
        UncertCalc.ThieleModulus(self)

      else: self.r = x['radius_f_particle (mm)'] / 2

      UncertCalc.Flow(self)
      UncertCalc.ResidenceTime(self)
      UncertCalc.RateConstants(self)
      UncertCalc.EffectivenessFactor(self)
      UncertCalc.TrueRateConstants(self)
      UncertCalc.Diffusivity(self)
      UncertCalc.Concentration(self)

    self.df = self.df.loc[~self.df["Trial"].isin(["34_coarse", "34_fine"])]
    for x in self.df["Metric"].unique():
      print('========', 
            f'{x} function: {self.functions[x]}',
            self.df.loc[self.df["Metric"] == x
                ].drop(['Input Uncert Value', 'Component Uncert', 'Metric', "Input Value"], axis=1
                ).set_index(["Trial", 'Total Uncert', 'Relative Uncert (%)', 'Variable']),
            sep='\n')


UncertCalc().All()