import pandas as pd
import pint

from math import log

uReg = pint.UnitRegistry(autoconvert_offset_to_baseunit = True)
uReg.default_format = "~P"
q = uReg.Quantity

# Design V-701, T-702, E-701, E702, C-701, and P-701 

class Heuristics:
    
    def T_702():
        '''
        Stream 7 -> T-702
            T-702 Bottoms -> Stream 9
            T-702 Tops -> Stream 10 + Stream 11
        '''
        flowF = q(7403.5, 'kmol/h')
        flowB = q(7141.7, 'kmol/h')
        flowD = flowF - flowB 
        presFeed = q(21, 'bar')
        
        def vapP(T, comp: bool = True): # True = water, False = etox
            if comp: a,b,c = 8.055729, 1723.6425115, 233.076427
            else : a,b,c = 7.274009, 1114.77883, 243.301237

            return q(10**(a - b / (T.to('degC').magnitude + c)), 'mmHg')
        
        ## not real numbers   
        x,y = 5,6
        t_ = q(70.2, 'degC')
        alpha = vapP(t_) / vapP(t_ , False)
        ##

        nMin = log((x / (1-x)) / ((y / (1-y)))) / log(alpha) 
        print(alpha, nMin, sep='\n')
        
    def V_701():
        pass

    def P_701():
        flow = q(182.75, 'kg/min')
        density = q(842.25, 'kg/m**3')
        dP = q(21 - 4.9, 'bar')

        power = q(1.67 
                 * (flow / density).to('m**3/min').magnitude 
                 * dP.magnitude, 'kW')
        
        head = (dP / (density * q(1, 'standard_gravity'))).to('ft')

        shaftEff =  (flow / density * (.7 - .45) / q(500  - 100, 'gal/min') + .7)
        shaftPower = power / shaftEff
        powerMotor = shaftPower / .8 

        print(
            '=== Calculations for unit P-701 ===', 
            f"fluid power: {power}", 
            f"fluid head: {head}", 
            f"shaft power: {shaftPower}",
            f"Power, motor: {powerMotor}",
            sep='\n')

    def HeatX(unit, th1, th2, tc1, tc2, Q, U, F):
        Tlm = ((th1 - tc2) - (th2 - tc1)) / log((th1 - tc2) / (th2 - tc1))
        a = (Q / (U * F * Tlm)).to('m**2')
        
        print(f"=== Calculations for unit {unit} ===",
            f'dTlm: {Tlm}',
            f"Area: {a}", 
            sep='\n'
        )

    def Equipment():
        Heuristics.HeatX( # Table 11.11
            'E-701',
            q(60.2, 'degC'), # th1, stream-3
            q(150, 'degC'), # th2, stream-4
            q(30, 'degC'), # tc1
            q(45, 'degC'), # tc2
            q(61400, 'MJ/h'), # Q, given
            q(1140, 'W/m**2/delta_degC'), # U, item 8
            .9, # F, item 1
        )
        
        Heuristics.HeatX( # Table 11.11
            'E-702',
            q(224.6, 'degC'), # th1, stream-5
            q(68.5, 'degC'), # th2, stream-6
            q(30, 'degC'), # tc1
            q(45, 'degC'), # tc2
            q(113300, 'MJ/h'), # Q, given
            q(850, 'W/m**2/delta_degC'), # U, item 8
            .9 # F, item 1
        )

        Heuristics.P_701()

Heuristics.Equipment()