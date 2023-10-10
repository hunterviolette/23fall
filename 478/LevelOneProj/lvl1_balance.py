import pandas as pd

# python -c "from lvl1_balance import LevelOneBalance as l; l().Tables()"

import pint
uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"

uReg.define('MMBtu = 1e6 * Btu')
uReg.define('lbmol = 453.592 * mol')
uReg.define('SCFM = ft**3 / min')
uReg.define('SCFH = ft**3 / h')

q = uReg.Quantity

class LevelOneBalance:

  def __init__(self) -> None:
    self.streamIndices = ['COMBAIR', 'FUEL', 'WETBRD', 'DRYBRD', 'EXHAUST']
    self.streamComponents = ['CH4', 'CO2', 'N2', 'O2', 'H2O', 'WOOD']

    self.scfh_to_mol = q(22.4 / 28.317, 'ft**3/mol')

    self.wetBoard_flow = q( 7.3e4, 'lb/hour')
    self.xBoard_reagant = .49

    self.fuel_flow = q( 6.83e4, 'SCFH')
    self.combAir_flow = q( 2.25e4, 'SCFM')

    self.exhaust_flow = q( 7.74e4, 'SCFM')

    self.MolecWeights = {
                      "CH4": q(16, 'lb / lbmol'),
                      "CO2": q(44, 'lb / lbmol'),
                      "N2": q(28, 'lb / lbmol'),
                      "O2": q(32, 'lb / lbmol'),
                      "H2O": q(18, 'lb / lbmol'),
                      "WOOD": q(1, 'lb / lbmol'),
                    }

    print('=== Knowns ===',
          f"Wetboard inlet flow: {self.wetBoard_flow} at {self.xBoard_reagant} consistency",
          f"Fuel gas flow: {self.fuel_flow}",
          f"Combustion air flow: {self.combAir_flow}",
          f"Exhaust air flow: {self.exhaust_flow}",
        sep='\n')

  def StreamConditions(self):
    
    moleFlow_combAir = (self.combAir_flow / self.scfh_to_mol).to('lbmol/h').magnitude
    moleFlow_fuel = (self.fuel_flow / self.scfh_to_mol).to('lbmol/h')
    massFlow_fuel = float(round((moleFlow_fuel * self.MolecWeights["CH4"]).magnitude, 3))

    self.woodFlow = (self.wetBoard_flow * self.xBoard_reagant) / self.MolecWeights["WOOD"]
    self.waterFlow = (self.wetBoard_flow * (1 - self.xBoard_reagant)) / self.MolecWeights["H2O"]
    self.moleFlow_wetbrd = self.woodFlow + self.waterFlow

    stream_df = pd.DataFrame(
        data=[
          [75, 0, 1, 0, moleFlow_combAir, self.combAir_flow.to('SCFH').magnitude, 0],
          [75, 0, 1, massFlow_fuel, moleFlow_fuel.magnitude, self.fuel_flow.magnitude, 0],
          [122, 0, 0, self.wetBoard_flow.magnitude, float(self.moleFlow_wetbrd.magnitude), 0, 0],
          [190, 0, 0, 0, float((self.woodFlow + self.waterFlow * .045).magnitude) , 0, 0],
          [310, 152, 1, 0, 0, self.exhaust_flow.to('SCFH').magnitude, 0],
        ],
        columns=['Temperature (degF)', 
                'Wet Bulb Temperature (degF)', 
                'Vapor Fraction', 
                'Mass Flow (lb/h)',
                'Mole Flow (lbmol/h)', 
                'Volume Flow (SCFH)', 
                'Enthalpy Flow (MMBtu/h)'
              ],
        index=self.streamIndices,
    ).round(4)

    self.stream_df = stream_df

  def MoleFractions(self):
    
    xH2O = float(q(.0293, 'atm') / q(1, 'atm') * .8)
    xO2 = .21 * (1 - xH2O)
    

    moleFrac_df = pd.DataFrame(
      data=[
        [0, 0, 1 - xH2O - xO2, xO2, xH2O, 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, float(self.waterFlow / self.moleFlow_wetbrd), float(self.woodFlow / self.moleFlow_wetbrd)],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 1 - xH2O - xO2, xO2, xH2O, 0],
      ],
      columns=self.streamComponents,
      index=self.streamIndices
    ).round(4)

    moleFrac_df["sum"] = moleFrac_df.sum(axis=1)
    self.moleFrac_df = moleFrac_df

  def MassFractions(self):
    
    caMoleFlow = self.stream_df.at["COMBAIR", 'Mole Flow (lbmol/h)']
    caMoleComps = self.moleFrac_df.loc[self.moleFrac_df.index == 'COMBAIR']
    
    n2Mass = q(caMoleFlow,'lbmol/h') * caMoleComps.at["COMBAIR","N2"] * self.MolecWeights["N2"]
    o2Mass = q(caMoleFlow,'lbmol/h') * caMoleComps.at["COMBAIR","O2"] * self.MolecWeights["O2"]
    h2oMass = q(caMoleFlow,'lbmol/h') * caMoleComps.at["COMBAIR","H2O"] * self.MolecWeights["H2O"]
    caMass = n2Mass + o2Mass + h2oMass

    self.stream_df.loc[self.stream_df.index == "COMBAIR", 'Mass Flow (lb/h)'] = float(round(caMass.magnitude, 3))

    massFrac_df = pd.DataFrame(
      data=[
        [0, 0, float(n2Mass / caMass), float(o2Mass / caMass), float(h2oMass/caMass), 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, .51, .49],
        [0, 0, 0, 0, .045, 1 - .045],
        [0, 0, 0, 0, 0, 0],
      ],
      columns=self.streamComponents,
      index=self.streamIndices
    ).round(4)

    '''print(self.waterFlow *, self.woodFlow)

    drybrd_MoleFlow = self.stream_df.at["DRYBRD", 'Mole Flow (lbmol/h)']
    self.stream_df.loc[self.stream_df.index == "DRYBRD", 'Mass Flow (lb/h)'
                      ] = ((drybrd_MoleFlow - self.woodFlow)  * self.MolecWeights["H2O"] + 
                           (self.woodFlow * self.MolecWeights["WOOD"]  
                          )'''


    massFrac_df["sum"] = massFrac_df.sum(axis=1)
    self.massFrac_df = massFrac_df

  def MoleFlows(self):
    pass

  def MassFlows(self):
    pass
    
  def Tables(self):
    LevelOneBalance.StreamConditions(self)
    LevelOneBalance.MoleFractions(self)
    LevelOneBalance.MassFractions(self)

    print(f"=== Stream Table ===", self.stream_df,
          '=== Mole Fractions Table ===', self.moleFrac_df,
          '=== Mass Fractions Table ===', self.massFrac_df,  
        sep='\n')