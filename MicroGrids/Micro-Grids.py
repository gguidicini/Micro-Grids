# -*- coding: utf-8 -*-
#billy rioja

from pyomo.environ import  AbstractModel

from Results import Plot_Energy_Total, Load_Results, Integer_Time_Series, Print_Results
from Model_Creation import Model_Creation
from Model_Resolution import Model_Resolution
from Import_Inputs import Renewable_Outputs    

# Type of problem formulation:
formulation = 'LP'

#Renewable_Outputs() # comment this line for computational speed once executed the first time
                    # OR if the renewable outputs yearly data are already available

Optimization_Goal = 'Variable cost' # Options: NPC / Variable cost 
Renewable_Penetration = 0.6 # a number from 0 to 1.
Battery_Independency = 0  # number of days of battery independency

model = AbstractModel() # define type of optimization problem

if formulation == 'LP':
    # Optimization model    
    Model_Creation(model,Optimization_Goal, Renewable_Penetration, Battery_Independency) # Creation of the Sets, parameters and variables.
    instance = Model_Resolution(model,Optimization_Goal,Renewable_Penetration,
                                Battery_Independency) # Resolution of the instance

    ## Upload the results from the instance and saving it in excel files
    Data = Load_Results(instance, Optimization_Goal) # Extract the results of energy from the instance and save it in a excel file 
    NPC = Data[0]
    Scenarios =  Data[2]
    Scenario_Probability = Data[4]
    Generator_Data = Data[3]
    Data_Renewable = Data[6]
    Battery_Data = Data[1]
    LCOE = Data[5]
    TotVarCost = Data[7]
     
# Energy Plot    
S = 1 # Plot scenario
Plot_Date = '21/03/2017 00:00:00' # Day-Month-Year ####ACTUALLY IT WILL INTERPRET A DATE PREFERABLY AS MONTH-DAY; IF DEVOID OF MEANING, IT WILL TRY DAY-MONTH
PlotTime = 1# Days of the plot
Time_Series = Integer_Time_Series(instance,Scenarios, S) 
   
plot = 'No Average' # 'No Average' or 'Average'
Plot_Energy_Total(instance, Time_Series, plot, Plot_Date, PlotTime)

Print_Results(LCOE, NPC, TotVarCost)  


