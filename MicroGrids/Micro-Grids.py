# -*- coding: utf-8 -*-
#billy rioja

import pandas as pd
from pyomo.environ import  AbstractModel

from Results import Plot_Energy_Total, Load_results1, Integer_Time_Series, Print_Results
from Model_Creation import Model_Creation, Model_Creation_binary, Model_Creation_Integer, Model_Creation_Dispatch
from Model_Resolution import Model_Resolution, Model_Resolution_binary, Model_Resolution_Integer, Model_Resolution_Dispatch
    

# Type of problem formulation:
formulation = 'LP'

Renewable_Penetration = 0.6 # a number from 0 to 1.
Battery_Independency = 0  # number of days of battery independency

model = AbstractModel() # define type of optimization problem

if formulation == 'LP':
    # Optimization model    
    Model_Creation(model, Renewable_Penetration, Battery_Independency) # Creation of the Sets, parameters and variables.
    instance = Model_Resolution(model,Renewable_Penetration,
                                Battery_Independency) # Resolution of the instance


    ## Upload the resulst from the instance and saving it in excel files
    Data = Load_results1(instance) # Extract the results of energy from the instance and save it in a excel file 
    NPC = Data[0]
    Scenarios =  Data[2]
    Scenario_Probability = Data[4]
    Generator_Data = Data[3]
    Data_Renewable = Data[6]
    Battery_Data = Data[1]
    LCOE = Data[5]
     
# Energy Plot    
S = 1 # Plot scenario
Plot_Date = '21/03/2017 00:00:00' # Day-Month-Year ####ACTUALLY IT WILL INTERPRET A DATE PREFERABLY AS MONTH-DAY; IF DEVOID OF MEANING, IT WILL TRY DAY-MONTH
PlotTime = 1# Days of the plot
Time_Series = Integer_Time_Series(instance,Scenarios, S) 
   
plot = 'No Average' # 'No Average' or 'Average'
Plot_Energy_Total(instance, Time_Series, plot, Plot_Date, PlotTime)

Print_Results(LCOE, NPC)  


