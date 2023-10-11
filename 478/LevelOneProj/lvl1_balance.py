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
    self.streamCols = [
                'Temperature (degF)', 
                'Wet Bulb Temperature (degF)', 
                'Vapor Fraction', 
                'Mass Flow (lb/h)',
                'Mole Flow (lbmol/h)', 
                'Volume Flow (SCFH)', 
                'Enthalpy Flow (MMBtu/h)'
              ]

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
    moleFlow_exhuast = (self.exhaust_flow / self.scfh_to_mol).to('lbmol/h')
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
          [310, 152, 1, 0, moleFlow_exhuast.magnitude, self.exhaust_flow.to('SCFH').magnitude, 0],
        ],
        columns=self.streamCols,
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
        [0, 0, 0, 0, 0, 0],
      ],
      columns=self.streamComponents,
      index=self.streamIndices
    ).round(4)

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
    
    drybrd_MassFlow = self.woodFlow * self.MolecWeights["WOOD"] / (1 - .045)

    self.stream_df.loc[self.stream_df.index == "DRYBRD", 'Mass Flow (lb/h)'
                      ] = float(drybrd_MassFlow.magnitude)
    
    woodMassFlow = self.woodFlow * self.MolecWeights["WOOD"]
    waterMassFlow = drybrd_MassFlow - woodMassFlow

    woodMoles = woodMassFlow / self.MolecWeights["WOOD"]
    waterMoles = waterMassFlow / self.MolecWeights["H2O"]

    self.moleFrac_df.loc[self.moleFrac_df.index == 'DRYBRD', 
                        'WOOD'] = float(round(woodMoles / (woodMoles + waterMoles), 3))
    
    self.moleFrac_df.loc[self.moleFrac_df.index == 'DRYBRD', 
                        'H2O'] = float(round(waterMoles / (woodMoles + waterMoles), 3))
    
    self.massFrac_df = massFrac_df

  def ExhaustMoleFractions(self):
    LevelOneBalance.StreamConditions(self)
    LevelOneBalance.MoleFractions(self)
    LevelOneBalance.MassFractions(self)

    caMoleFlow = self.stream_df.at["COMBAIR", "Mole Flow (lbmol/h)"]
    fMoleFlow = self.stream_df.at["FUEL", "Mole Flow (lbmol/h)"]

    df = self.moleFrac_df

    o2Moles = df.at["COMBAIR", 'O2'] * caMoleFlow 
    outletFlow = fMoleFlow + caMoleFlow

    self.moleFrac_df = pd.concat([
      df,
      pd.DataFrame({
        "CH4":[0], 
        "CO2": [fMoleFlow / outletFlow],
        "N2": [df.at["COMBAIR", 'N2'] * caMoleFlow / outletFlow],
        "O2": [(o2Moles - 2*fMoleFlow)  / outletFlow],
        "H2O": [((df.at["COMBAIR", 'H2O'] * caMoleFlow) + 2 * fMoleFlow) / outletFlow],
        "WOOD": [0],
      }, index=["BOILER_OUTLET"])
    ], axis=0)
    
    self.stream_df = pd.concat([
      self.stream_df,
      pd.DataFrame(data=[
                    [0, 0, 1, 0, outletFlow, 0 ,0]
                  ],
                  columns=self.streamCols,
                  index=["BOILER_OUTLET"]
                  )
    ])

    waterEvap = (
      self.stream_df.at["WETBRD", 'Mole Flow (lbmol/h)'] -
      self.stream_df.at["DRYBRD", 'Mole Flow (lbmol/h)']
    )

    molesIn = (
          self.stream_df.at["BOILER_OUTLET", 'Mole Flow (lbmol/h)'] +
          self.stream_df.at["WETBRD", 'Mole Flow (lbmol/h)']
        )
    
    molesOut = (
          self.stream_df.at["DRYBRD", 'Mole Flow (lbmol/h)'] +
          self.stream_df.at["EXHAUST", 'Mole Flow (lbmol/h)']
    )
    
    self.molesAir = round(molesOut - molesIn, 3)

    molesBoiler = self.stream_df.at["BOILER_OUTLET", "Mole Flow (lbmol/h)"]

    molh2o = waterEvap + (
              self.moleFrac_df.at["BOILER_OUTLET", "H2O"] * molesBoiler
              ) + self.moleFrac_df.at["COMBAIR", "H2O"] * self.molesAir
    
    molco2 = (self.moleFrac_df.at["BOILER_OUTLET", "CO2"] * molesBoiler
              ) + self.moleFrac_df.at["COMBAIR", "CO2"] * self.molesAir
    
    moln2 = (self.moleFrac_df.at["BOILER_OUTLET", "N2"] * molesBoiler
              ) + self.moleFrac_df.at["COMBAIR", "N2"] * self.molesAir
    
    molo2 = (self.moleFrac_df.at["BOILER_OUTLET", "O2"] * molesBoiler
              ) + self.moleFrac_df.at["COMBAIR", "O2"] * self.molesAir
    
    exhuastMoles = molh2o + molco2 + moln2 + molo2

    for x in ["CO2", "N2", "O2", "H2O"]:
      molDict = {"CO2": molco2, "N2": moln2,
                "O2": molo2, "H2O": molh2o}

      self.moleFrac_df.loc[self.moleFrac_df.index == 'EXHAUST',
                          x] = molDict[x] / exhuastMoles
      
    
    self.moleFrac_df["sum"] = self.moleFrac_df.sum(axis=1)

  def ExhaustMassFractions(self):
    LevelOneBalance.ExhaustMoleFractions(self)

    molFlow = q(self.stream_df.at["EXHAUST", "Mole Flow (lbmol/h)"], 'lbmol/h')
    molFrac = self.moleFrac_df.loc[self.moleFrac_df.index == "EXHAUST"]

    co2Mass = molFlow * molFrac.at["EXHAUST", "CO2"] * self.MolecWeights["CO2"]
    n2Mass = molFlow * molFrac.at["EXHAUST", "N2"] * self.MolecWeights["N2"]
    o2Mass = molFlow * molFrac.at["EXHAUST", "O2"] * self.MolecWeights["O2"]
    h2oMass = molFlow * molFrac.at["EXHAUST", "H2O"] * self.MolecWeights["H2O"]

    totalMass = co2Mass + n2Mass + o2Mass + h2oMass

    for x in ["CO2", "N2", "O2", "H2O"]:
      massDict = {"CO2": co2Mass, "N2": n2Mass,
                "O2": o2Mass, "H2O": h2oMass}

      self.massFrac_df.loc[self.massFrac_df.index == 'EXHAUST',
                          x] = (massDict[x] / totalMass).magnitude

    self.massFrac_df["sum"] = self.massFrac_df.sum(axis=1)
  
    self.stream_df.at["EXHAUST", "Mass Flow (lb/h)"] = totalMass.magnitude

  def Tables(self):
    LevelOneBalance.ExhaustMassFractions(self)

    print("=== Stream Table ===", self.stream_df,
          '=== Moles of Air Missing (lbmol/h) ===', self.molesAir,
          '=== Mole Fractions Table ===', self.moleFrac_df,
          '=== Mass Fractions Table ===', self.massFrac_df,  
          '===========',
        sep='\n')
