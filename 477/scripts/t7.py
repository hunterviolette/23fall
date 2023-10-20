import pint
uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"

uReg.define('dollar = [currency] = dollar')
uReg.define('thousand_dollar = 10**3 * dollar')
uReg.define('million_dollar = 10**6 * dollar')


q = uReg.Quantity


class PlantCalc:
    
    def __init__(self) -> None:
        
        self.streamFactor = .92
        self.molecWeights = {
            "Isopropyl Alcohol": q(60.1, 'g/mol'),
            "Acetone": q(58.08, 'g/mol'),
            "Water": q(18.02, 'g/mol'),
        }
        
    def Streams(self):
        
        ipaCost = q(1.44, 'dollar/kg') * q(2670, 'kg/hr')
        waterCost = q(360, 'kg/hr') * q(14.5 / 1000, 'dollar/kg')
        
        feedCost = (ipaCost + waterCost).to('million_dollar/year').__round__(2)
        
        acetoneRev = q(1860, 'kg/hr') * q(2.9, 'dollar/kg')
        gasRev = q(240, 'kg/hr') * q(.5, 'dollar/kg')
        
        revenue = (acetoneRev + gasRev).to('million_dollar/year').__round__(2)
        
        gross_profit = ((revenue - feedCost) * self.streamFactor).__round__(2)
        
        print(f"Feed Cost: {feedCost}",
              f"Revenue: {revenue}",
              f"Gross Profit: {gross_profit}",
              sep='\n')
        
PlantCalc().Streams()