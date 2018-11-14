import numpy as np

# Objective funtion

def Net_Present_Cost(model): # OBJETIVE FUNTION: MINIMIZE THE NPC FOR THE SISTEM
    '''
    This function computes the sum of the multiplication of the net present cost 
    NPC (USD) of each scenario and their probability of occurrence.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
      
    return (sum(model.Scenario_Net_Present_Cost[s]*model.Scenario_Weight[s] for s in model.scenario ))
           
##################################################### PV constraints##################################################

def Renewable_Energy(model,s,r,t): # Energy output of the solar panels
    '''
    This constraint calculates the energy produce by the solar panels taking in 
    account the efficiency of the inverter for each scenario.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Total_Energy_Renewable[s,r,t] == model.Renewable_Energy_Production[s,r,t]*model.Renewable_Inverter_Efficiency[r]*model.Renewable_Units[r]

#################################################### Battery constraints #############################################

def State_of_Charge(model,s,y,t): # State of Charge of the battery
    '''
    This constraint calculates the State of charge of the battery (State_Of_Charge) 
    for each period of analysis. The State_Of_Charge is in the period 't' is equal to
    the State_Of_Charge in period 't-1' plus the energy flow into the battery, 
    minus the energy flow out of the battery. This is done for each scenario s.
    In time t=1 the State_Of_Charge_Battery is equal to a fully charged battery.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    if t==1 and y==1: # The state of charge (State_Of_Charge) for the period 0 is equal to the Battery size.
        return model.State_Of_Charge_Battery[s,y,t] == model.Battery_Nominal_Capacity*model.Battery_Initial_SOC - model.Energy_Battery_Flow_Out[s,y,t]/model.Discharge_Battery_Efficiency + model.Energy_Battery_Flow_In[s,y,t]*model.Charge_Battery_Efficiency
    if t==1 and y!=1:
        return model.State_Of_Charge_Battery[s,y,t] == model.State_Of_Charge_Battery[s,y-1,model.Periods] - model.Energy_Battery_Flow_Out[s,y,t]/model.Discharge_Battery_Efficiency + model.Energy_Battery_Flow_In[s,y,t]*model.Charge_Battery_Efficiency
    else:  
        return model.State_Of_Charge_Battery[s,y,t] == model.State_Of_Charge_Battery[s,y,t-1] - model.Energy_Battery_Flow_Out[s,y,t]/model.Discharge_Battery_Efficiency + model.Energy_Battery_Flow_In[s,y,t]*model.Charge_Battery_Efficiency    

def Maximun_Charge(model,s,y,t): # Maximun state of charge of the Battery
    '''
    This constraint keeps the state of charge of the battery equal or under the 
    size of the battery for each scenario s.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.State_Of_Charge_Battery[s,y,t] <= model.Battery_Nominal_Capacity

def Minimun_Charge(model,s,y,t): # Minimun state of charge
    '''
    This constraint maintains the level of charge of the battery above the deep 
    of discharge in each scenario i.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.State_Of_Charge_Battery[s,y,t] >= model.Battery_Nominal_Capacity*model.Deep_of_Discharge

def Max_Power_Battery_Charge(model): 
    '''
    This constraint calculates the Maximum power of charge of the battery. Taking in account the 
    capacity of the battery and a time frame in which the battery has to be fully loaded for 
    each scenario.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Maximun_Charge_Power== model.Battery_Nominal_Capacity/model.Maximun_Battery_Charge_Time

def Max_Power_Battery_Discharge(model):
    '''
    This constraint calculates the Maximum power of discharge of the battery. for 
    each scenario i.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Maximun_Discharge_Power == model.Battery_Nominal_Capacity/model.Maximun_Battery_Discharge_Time

def Max_Bat_in(model,s,y,t): # Minimun flow of energy for the charge fase
    '''
    This constraint maintains the energy in to the battery, below the maximum power 
    of charge of the battery for each scenario s.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Energy_Battery_Flow_In[s,y,t] <= model.Maximun_Charge_Power*model.Delta_Time

def Max_Bat_out(model,s,y,t): #minimun flow of energy for the discharge fase
    '''
    This constraint maintains the energy from the battery, below the maximum power of 
    discharge of the battery for each scenario s.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Energy_Battery_Flow_Out[s,y,t] <= model.Maximun_Discharge_Power*model.Delta_Time


############################################## Energy Constraints ##################################################

def Energy_balance(model,s,y,t): # Energy balance
    '''
    This constraint ensures the perfect match between the energy energy demand of the 
    system and the differents sources to meet the energy demand each scenario s.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    
    Foo = []
    for r in model.renewable_source:
        Foo.append((s,r,t))
    
    Total_Renewable_Energy = sum(model.Total_Energy_Renewable[j] for j in Foo)
    
    foo=[]
    for g in model.generator_type:
        foo.append((s,y,g,t))
    
    Generator_Energy = sum(model.Generator_Energy[i] for i in foo)  

    return model.Energy_Demand[s,y,t] == (Total_Renewable_Energy + Generator_Energy 
            - model.Energy_Battery_Flow_In[s,y,t] + model.Energy_Battery_Flow_Out[s,y,t] 
            + model.Lost_Load[s,y,t] - model.Energy_Curtailment[s,y,t])

def Maximun_Lost_Load(model,s,y): # Maximum permissible lost load
    '''
    This constraint ensures that the ratio between the lost load and the energy 
    Demand does not exceeds the value of the permissible lost load each scenario s. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Lost_Load_Probability >= (sum(model.Lost_Load[s,y,t] for t in model.periods)/sum(model.Energy_Demand[s,y,t] for t in model.periods))


######################################## Diesel generator constraints ############################

def Maximun_Generator_Energy(model,s,y,g,t): # Maximun energy output of the diesel generator
    '''
    This constraint ensures that the generator will not exceed his nominal capacity 
    in each period in each scenario s.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Generator_Energy[s,y,g,t] <= model.Generator_Nominal_Capacity[g]*model.Delta_Time


########################################### Economical Constraints ###################################################

def Fuel_Cost_Total(model,s,g):
    '''
    This constraint calculate the total cost due to the used of diesel to generate 
    electricity in the generator in each scenario s. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''    
#    foo=[]
#    for y in range(1,model.Years+1):
#        for t in range(1,model.Periods+1):
#            foo.append((s,y,g,t))
    Fuel_Cost_Tot = 0
    for y in range(1, model.Years +1):
        Num = sum(model.Generator_Energy[s,y,g,t]*model.Marginal_Cost_Generator_1[g] for t in model.periods)
        Fuel_Cost_Tot += Num/((1+model.Discount_Rate)**y)
    return model.Fuel_Cost_Total[s,g] == Fuel_Cost_Tot
    
def Scenario_Lost_Load_Cost(model,s):
    '''
    This constraint calculate the cost due to the lost load in each scenario s. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
#    foo=[]
#    for y in range(1,model.Years+1):
#        for t in range(1,model.Periods+1):
#            foo.append((s,y,t))
    Cost_Lost_Load = 0         
    for y in range(1, model.Years +1):
        Num = sum(model.Lost_Load[s,y,t]*model.Value_Of_Lost_Load for t in model.periods)
        Cost_Lost_Load += Num/((1+model.Discount_Rate)**y)

    return  model.Scenario_Lost_Load_Cost[s] == Cost_Lost_Load
 
      
def Initial_Inversion(model):
    '''
    This constraint calculate the initial inversion for the system. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''    
    
    Inv_Ren = sum(model.Renewable_Units[r]*model.Renewable_Nominal_Capacity[r]*model.Renewable_Invesment_Cost[r] for r in model.renewable_source)
    Inv_Gen = sum(model.Generator_Invesment_Cost[g]*model.Generator_Nominal_Capacity[g] for g in model.generator_type)
    return model.Initial_Inversion == (Inv_Ren + Inv_Gen
                 + model.Battery_Nominal_Capacity*model.Battery_Invesment_Cost)

def Operation_Maintenance_Cost(model):
    '''
    This funtion calculate the operation and maintenance for the system. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''    
    OyM_Ren = sum(model.Renewable_Units[r]*model.Renewable_Nominal_Capacity[r]*model.Renewable_Invesment_Cost[r]*model.Maintenance_Operation_Cost_Renewable[r] for r in model.renewable_source)
    OyM_Gen = sum(model.Generator_Invesment_Cost[g]*model.Generator_Nominal_Capacity[g]*model.Maintenance_Operation_Cost_Generator[g] for g in model.generator_type)
    return model.Operation_Maintenance_Cost == sum(((OyM_Ren + model.Battery_Nominal_Capacity*model.Battery_Invesment_Cost*model.Maintenance_Operation_Cost_Battery+OyM_Gen)/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years) 

    
def Battery_Reposition_Cost(model,s):
    '''
    This funtion calculate the reposition of the battery after a stated time of use. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    
    '''
    
    Battery_cost_in = [0 for y in model.years]
    Battery_cost_out = [0 for y in model.years]
    Battery_Yearly_cost = [0 for y in model.years]
    
#    foo=[]
    for y in range(1,model.Years+1):
#        for t in range(1,model.Periods+1):
#                foo.append((s,y,t))    
            
    
        Battery_cost_in[y-1] = sum(model.Energy_Battery_Flow_In[s,y,t]*model.Unitary_Battery_Reposition_Cost for t in model.periods)
        Battery_cost_out[y-1] = sum(model.Energy_Battery_Flow_Out[s,y,t]*model.Unitary_Battery_Reposition_Cost for t in model.periods)
        Battery_Yearly_cost[y-1] = Battery_cost_in[y-1] + Battery_cost_out[y-1]

    return model.Battery_Reposition_Cost[s] == sum(Battery_Yearly_cost[y-1]/((1+model.Discount_Rate)**model.Project_Years[y]) for y in model.years) 
    
    
def Scenario_Net_Present_Cost(model,s): 
    '''
    This function computes the Net Present Cost for the life time of the project, taking in account that the 
    cost are fix for each year.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''            
    foo = []
    for g in range(1,model.Generator_Type+1):
            foo.append((s,g))
            
    Fuel_Cost = sum(model.Fuel_Cost_Total[s,g] for s,g in foo)
    
    return model.Scenario_Net_Present_Cost[s] == (model.Initial_Inversion + model.Operation_Maintenance_Cost + model.Battery_Reposition_Cost[s] 
            + model.Scenario_Lost_Load_Cost[s] + Fuel_Cost)     # Fuel_Cost depends on s
                
    
def Renewable_Energy_Penetration(model):
    
    Foo=[]
    for s in range(1, model.Scenarios + 1):
        for y in range(1, model.Years +1):
            for g in range(1, model.Generator_Type+1):
                for t in range(1,model.Periods+1):
                    Foo.append((s,y,g,t))    
                    
    foo=[]
    for s in range(1, model.Scenarios + 1):
        for r in range(1, model.Renewable_Source+1):
            for t in range(1,model.Periods+1):
                foo.append((s,r,t))    
    
    E_gen = sum(model.Generator_Energy[s,y,g,t]*model.Scenario_Weight[s]
                for s,y,g,t in Foo)
    
    E_ren = sum(model.Total_Energy_Renewable[s,r,t]*model.Scenario_Weight[s]
                for s,r,t in foo)*model.Years
        
    return  (1 - model.Renewable_Penetration)*E_ren >= model.Renewable_Penetration*E_gen   


def Battery_Min_Capacity(model):
    
       
    return   model.Battery_Nominal_Capacity >= model.Battery_Min_Capacity


