
import pandas as pd
import pyomo.environ 
import re

def Initialize_years(model, y):

    '''
    This function returns the value of each year of the project. 
    
    :param model: Pyomo model as defined in the Model_Creation script.
    
    :return: The year y.
    '''    
    return y

# This section extracts the values of Scenarios, Periods, Years from data.dat
# and creates ranges for them
Data_file = "Example/Data.dat"
Data_import = open(Data_file).readlines()

n_scenarios = int((re.findall('\d+',Data_import[34])[0]))
n_years = int((re.findall('\d+',Data_import[2])[0]))
n_periods = int((re.findall('\d+',Data_import[0])[0]))

scenario = [i for i in range(1,n_scenarios+1)]
year = [i for i in range(1,n_years+1)]
period = [i for i in range(1,n_periods+1)]


# This section imports the multi-year Demand and creates a Multi-indexed pd.DataFrame for it
Demand = pd.read_excel('Example/Demand.xls')

<<<<<<< HEAD
Energy_Demand_Series = pd.Series()

for i in range(1,n_years*n_scenarios+1):
=======
rows = Demand.shape[0]
columns = Demand.shape[1]
Energy_Demand_Series = pd.Series()

for i in range(1,columns+1):
>>>>>>> ed31ae9a58c1245e3b9e1040121ea73e285c0bca
    dum = Demand[i][:]
    Energy_Demand_Series = pd.concat([Energy_Demand_Series,dum])

Energy_Demand = pd.DataFrame(Energy_Demand_Series) 
frame = [scenario,year,period]
index = pd.MultiIndex.from_product(frame, names=['scenario','year','period'])
Energy_Demand.index = index


# This section creates a pd.DataFrame which stores the multi-year demand of each scenario
# in a different column (used in Initialize: Min_Bat_Capacity)
Energy_Demand_2 = pd.DataFrame()    

for s in scenario:
    Energy_Demand_Series_2 = pd.Series()
    for y in year:
        dum_2 = Demand[(s-1)*n_years + y][:]
        Energy_Demand_Series_2 = pd.concat([Energy_Demand_Series_2,dum_2])
    Energy_Demand_2.loc[:,s] = Energy_Demand_Series_2

index_2 = pd.RangeIndex(1,n_years*n_periods+1)
Energy_Demand_2.index = index_2


def Initialize_Demand(model, s, y, t):
    '''
    This function returns the value of the energy demand from a system for each period of analysis from an excel file.
    
    :param model: Pyomo model as defined in the Model_Creation script.
        
    :return: The energy demand for the period t.     
        
    '''
    return float(Energy_Demand[0][(s,y,t)])

#PV_Energy = pd.read_excel('Example/PV_Energy.xls') # open the PV energy yield file
#
#def Initialize_PV_Energy(model, i, t):
#    '''
#    This function returns the value of the energy yield by one PV under the characteristics of the system 
#    analysis for each period of analysis from a excel file.
#    
#    :param model: Pyomo model as defined in the Model_Creation script.
#    
#    :return: The energy yield of one PV for the period t.
#    '''
#    return float(PV_Energy[i][t])

def Initialize_Demand_Dispatch(model, t):
    '''
    This function returns the value of the energy demand from a system for each period of analysis from a excel file.
    
    :param model: Pyomo model as defined in the Model_Creation script.
        
    :return: The energy demand for the period t.     
        
    '''
    return float(Energy_Demand[1][t])


def Initialize_PV_Energy_Dispatch(model, t):
    '''
    This function returns the value of the energy yield by one PV under the characteristics of the system 
    analysis for each period of analysis from a excel file.
    
    :param model: Pyomo model as defined in the Model_Creation script.
    
    :return: The energy yield of one PV for the period t.
    '''
    return float(PV_Energy[1][t])
    
    
def Marginal_Cost_Generator_1(model,g):
    
    return model.Fuel_Cost[g]/(model.Low_Heating_Value[g]*model.Generator_Efficiency[g])

#def Start_Cost(model,i):
#    
#    return #model.Marginal_Cost_Generator_1[i]*model.Generator_Nominal_Capacity[i]*model.Cost_Increase[i]
#
#def Marginal_Cost_Generator(model, i):
#    
#    return #(model.Marginal_Cost_Generator_1[i]*model.Generator_Nominal_Capacity[i]-model.Start_Cost_Generator[i])/model.Generator_Nominal_Capacity[i] 


def Capital_Recovery_Factor(model):
   
    a = model.Discount_Rate*((1+model.Discount_Rate)**model.Years)
    b = ((1 + model.Discount_Rate)**model.Years)-1
    return a/b

    
def Battery_Reposition_Cost(model):
   
    unitary_battery_cost = model.Battery_Invesment_Cost - model.Battery_Electronic_Invesmente_Cost
    return unitary_battery_cost/(model.Battery_Cycles*2*(1-model.Deep_of_Discharge))
    
    
Renewable_Energy = pd.read_excel('Example/Renewable_Energy.xls') # open the PV energy yield file

def Initialize_Renewable_Energy(model,s,r,t):
    '''
    This function returns the value of the energy yield by one PV under the characteristics of the system 
    analysis for each period of analysis from a excel file.
    
    :param model: Pyomo model as defined in the Model_Creation script.
    
    :return: The energy yield of one PV for the period t.
    '''
    column = (s-1)*model.Renewable_Source + r 
    return float(Renewable_Energy[column][t])   
    
    
    
def Marginal_Cost_Generator_1_Dispatch(model):
    
    return model.Diesel_Cost/(model.Low_Heating_Value*model.Generator_Efficiency)

def Start_Cost_Dispatch(model):
    
    return model.Marginal_Cost_Generator_1*model.Generator_Nominal_Capacity*model.Cost_Increase

def Marginal_Cost_Generator_Dispatch(model):
    
    return (model.Marginal_Cost_Generator_1*model.Generator_Nominal_Capacity-model.Start_Cost_Generator)/model.Generator_Nominal_Capacity 

def Min_Bat_Capacity(model):
        
    
    Periods = model.Battery_Independency*24
    Len = int(model.Periods*model.Years/Periods)
    Grouper = 1
    index = 1
    for i in range(1, Len+1):
        for j in range(1,Periods+1):
            
            Energy_Demand_2.loc[index, 'Grouper'] = Grouper
            index += 1
            
        Grouper += 1
            
    Period_Energy = Energy_Demand_2.groupby(['Grouper']).sum()
    
    Period_Average_Energy = Period_Energy.mean()
    
    Available_Energy = sum(Period_Average_Energy[s]*model.Scenario_Weight[s] 
        for s in model.scenario) 

    return  Available_Energy/(1-model.Deep_of_Discharge)

