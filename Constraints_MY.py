def Net_Present_Cost_Obj(model): 
    '''
    This function computes the sum of the multiplication of the net present cost 
    NPC (USD) of each scenario and their probability of occurrence.
    
    :param model: Pyomo model as defined in the Model_creation library.
    ''' 
    return (sum(model.Scenario_Net_Present_Cost[s]*model.Scenario_Weight[s] for s in model.scenarios))
    

def Net_Present_Cost(model): 
        
    return model.Net_Present_Cost == (sum(model.Scenario_Net_Present_Cost[s]*model.Scenario_Weight[s] for s in model.scenarios))


def Renewable_Energy(model,s,yt,ut,r,t): # Energy output of the solar panels
    '''
    This constraint calculates the energy produce by the solar panels taking in 
    account the efficiency of the inverter for each scenario.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Total_Renewable_Energy[s,yt,r,t] == model.Renewable_Energy_Production[s,r,t]*model.Renewable_Inverter_Efficiency[r]*model.Renewable_Units[ut,r]


def State_of_Charge(model,s,yt,ut,t): # State of Charge of the battery
    '''
    This constraint calculates the State of charge of the battery (State_Of_Charge) 
    for each period of analysis. The State_Of_Charge is in the period 't' is equal to
    the State_Of_Charge in period 't-1' plus the energy flow into the battery, 
    minus the energy flow out of the battery. This is done for each scenario s.
    In time t=1 the State_Of_Charge_Battery is equal to a fully charged battery.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    if t==1 and yt==1: # The state of charge (State_Of_Charge) for the period 0 is equal to the Battery size.
        return model.State_Of_Charge_Battery[s,yt,t] == model.Battery_Nominal_Capacity[ut]*model.Battery_Initial_SOC - model.Energy_Battery_Flow_Out[s,yt,t]/model.Discharge_Battery_Efficiency + model.Energy_Battery_Flow_In[s,yt,t]*model.Charge_Battery_Efficiency
    if t==1 and yt!=1:
        return model.State_Of_Charge_Battery[s,yt,t] == model.State_Of_Charge_Battery[s,yt-1,model.Periods] - model.Energy_Battery_Flow_Out[s,yt,t]/model.Discharge_Battery_Efficiency + model.Energy_Battery_Flow_In[s,yt,t]*model.Charge_Battery_Efficiency
    else:  
        return model.State_Of_Charge_Battery[s,yt,t] == model.State_Of_Charge_Battery[s,yt,t-1] - model.Energy_Battery_Flow_Out[s,yt,t]/model.Discharge_Battery_Efficiency + model.Energy_Battery_Flow_In[s,yt,t]*model.Charge_Battery_Efficiency    


def Maximun_Charge(model,s,yt,ut,t): # Maximun state of charge of the Battery
    '''
    This constraint keeps the state of charge of the battery equal or under the 
    size of the battery for each scenario s.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.State_Of_Charge_Battery[s,yt,t] <= model.Battery_Nominal_Capacity[ut]


def Minimun_Charge(model,s,yt,ut,t): # Minimun state of charge
    '''
    This constraint maintains the level of charge of the battery above the deep 
    of discharge in each scenario i.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.State_Of_Charge_Battery[s,yt,t] >= model.Battery_Nominal_Capacity[ut]*model.Depth_of_Discharge


def Max_Power_Battery_Charge(model,ut): 
    '''
    This constraint calculates the Maximum power of charge of the battery. Taking in account the 
    capacity of the battery and a time frame in which the battery has to be fully loaded for 
    each scenario.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Maximum_Charge_Power[ut] == model.Battery_Nominal_Capacity[ut]/model.Maximum_Battery_Charge_Time


def Max_Power_Battery_Discharge(model,ut):
    '''
    This constraint calculates the Maximum power of discharge of the battery. for 
    each scenario i.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Maximum_Discharge_Power[ut] == model.Battery_Nominal_Capacity[ut]/model.Maximum_Battery_Discharge_Time


def Max_Bat_in(model,s,yt,ut,t): # Minimun flow of energy for the charge fase
    '''
    This constraint maintains the energy in to the battery, below the maximum power 
    of charge of the battery for each scenario s.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Energy_Battery_Flow_In[s,yt,t] <= model.Maximum_Charge_Power[ut]*model.Delta_Time


def Max_Bat_out(model,s,yt,ut,t): #minimun flow of energy for the discharge fase
    '''
    This constraint maintains the energy from the battery, below the maximum power of 
    discharge of the battery for each scenario s.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Energy_Battery_Flow_Out[s,yt,t] <= model.Maximum_Discharge_Power[ut]*model.Delta_Time


def Energy_balance(model,s,yt,ut,t): # Energy balance
    '''
    This constraint ensures the perfect match between the energy energy demand of the 
    system and the differents sources to meet the energy demand each scenario s.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''  
    Foo = []
    for r in model.renewable_sources:
        Foo.append((s,yt,r,t))
    
    Total_Renewable_Energy = sum(model.Total_Renewable_Energy[j] for j in Foo)
    
    foo=[]
    for g in model.generator_types:
        foo.append((s,yt,g,t))
    
    Total_Generator_Energy = sum(model.Total_Generator_Energy[i] for i in foo)  

    return model.Energy_Demand[s,yt,t] == (Total_Renewable_Energy + Total_Generator_Energy 
                                      - model.Energy_Battery_Flow_In[s,yt,t] + model.Energy_Battery_Flow_Out[s,yt,t] 
                                      + model.Lost_Load[s,yt,t] - model.Energy_Curtailment[s,yt,t])


def Maximun_Lost_Load(model,s,yt): # Maximum permissible lost load
    '''
    This constraint ensures that the ratio between the lost load and the energy 
    Demand does not exceeds the value of the permissible lost load each scenario s. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    return model.Lost_Load_Probability >= (sum(model.Lost_Load[s,yt,t] for t in model.periods)/sum(model.Energy_Demand[s,yt,t] for t in model.periods))



def Maximun_Generator_Energy(model,s,yt,ut,g,t): # Maximun energy output of the diesel generator
    '''
    This constraint ensures that the generator will not exceed his nominal capacity 
    in each period in each scenario s.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''    
    return model.Total_Generator_Energy[s,yt,g,t] <= model.Generator_Nominal_Capacity[ut,g]*model.Delta_Time


def Total_Fuel_Cost_Act(model,s,g):
    '''
    This constraint calculate the total cost due to the used of diesel to generate 
    electricity in the generator in each scenario s. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''    
    Fuel_Cost_Tot = 0
    for y in range(1, model.Years +1):
        Num = sum(model.Total_Generator_Energy[s,y,g,t]*model.Generator_Marginal_Cost[s,y,g] for t in model.periods)
        Fuel_Cost_Tot += Num/((1+model.Discount_Rate)**y)
    return model.Total_Fuel_Cost_Act[s,g] == Fuel_Cost_Tot


def Total_Fuel_Cost_NonAct(model,s,g):
    '''
    This constraint calculate the total cost due to the used of diesel to generate 
    electricity in the generator in each scenario s. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''    
    Fuel_Cost_Tot = 0
    for y in range(1, model.Years +1):
        Num = sum(model.Total_Generator_Energy[s,y,g,t]*model.Generator_Marginal_Cost[s,y,g] for t in model.periods)
        Fuel_Cost_Tot += Num
    return model.Total_Fuel_Cost_NonAct[s,g] == Fuel_Cost_Tot
   
    
def Scenario_Lost_Load_Cost_Act(model,s):
    '''
    This constraint calculate the cost due to the lost load in each scenario s. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    Cost_Lost_Load = 0         
    for y in range(1, model.Years +1):
        Num = sum(model.Lost_Load[s,y,t]*model.Value_Of_Lost_Load for t in model.periods)
        Cost_Lost_Load += Num/((1+model.Discount_Rate)**y)

    return  model.Scenario_Lost_Load_Cost_Act[s] == Cost_Lost_Load
 
 
def Scenario_Lost_Load_Cost_NonAct(model,s):
    '''
    This constraint calculate the cost due to the lost load in each scenario s. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''
    Cost_Lost_Load = 0         
    for y in range(1, model.Years +1):
        Num = sum(model.Lost_Load[s,y,t]*model.Value_Of_Lost_Load for t in model.periods)
        Cost_Lost_Load += Num

    return  model.Scenario_Lost_Load_Cost_NonAct[s] == Cost_Lost_Load

     
def Investment_Cost(model):
    '''
    This constraint calculate the initial inversion for the system. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''    
    upgrade_years_list = [1 for i in range(len(model.upgrades))]
    s_dur = model.Step_Duration
   
    for i in range(1, len(model.upgrades)): 
        upgrade_years_list[i] = upgrade_years_list[i-1] + s_dur
    
    yu_tuples_list = [[] for i in model.years]
    
    for y in model.years:    
    
        for i in range(len(upgrade_years_list)-1):
            if y >= upgrade_years_list[i] and y < upgrade_years_list[i+1]:
                yu_tuples_list[y-1] = (y, model.upgrades[i+1])
            
            elif y >= upgrade_years_list[-1]:
                yu_tuples_list[y-1] = (y, len(model.upgrades))    
          
    tup_list = [[] for i in range(len(model.upgrades)-1)]
    
    for i in range(0, len(model.upgrades) - 1):
        tup_list[i] = yu_tuples_list[model.Step_Duration*i + model.Step_Duration]
        
    Inv_Ren = sum((model.Renewable_Units[1,r]*model.Renewable_Nominal_Capacity[r]*model.Renewable_Investment_Cost[r])
                    + sum((((model.Renewable_Units[ut,r] - model.Renewable_Units[ut-1,r])*model.Renewable_Nominal_Capacity[r]*model.Renewable_Investment_Cost[r]*model.Renewable_Inv_Cost_Reduction[r]))/((1+model.Discount_Rate)**(yt-1))
                    for (yt,ut) in tup_list) for r in model.renewable_sources)
    
    Inv_Gen = sum((model.Generator_Nominal_Capacity[1,g]*model.Generator_Investment_Cost[g])
                    + sum((((model.Generator_Nominal_Capacity[ut,g] - model.Generator_Nominal_Capacity[ut-1,g])*model.Generator_Investment_Cost[g]))/((1+model.Discount_Rate)**(yt-1))
                    for (yt,ut) in tup_list) for g in model.generator_types)
    
    Inv_Bat = ((model.Battery_Nominal_Capacity[1]*model.Battery_Investment_Cost)
                    + sum((((model.Battery_Nominal_Capacity[ut] - model.Battery_Nominal_Capacity[ut-1])*model.Battery_Investment_Cost))/((1+model.Discount_Rate)**(yt-1))
                    for (yt,ut) in tup_list))
    
    return model.Investment_Cost == Inv_Ren + Inv_Gen + Inv_Bat


def Operation_Maintenance_Cost_Act(model):
    '''
    This funtion calculate the operation and maintenance for the system. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''    
    OyM_Ren = sum(sum((model.Renewable_Units[ut,r]*model.Renewable_Nominal_Capacity[r]*model.Renewable_Investment_Cost[r]*model.Renewable_Operation_Maintenance_Cost[r])/((
                    1+model.Discount_Rate)**yt)for (yt,ut) in model.yu_tup)for r in model.renewable_sources)
    
    OyM_Gen = sum(sum((model.Generator_Nominal_Capacity[ut,g]*model.Generator_Investment_Cost[g]*model.Generator_Operation_Maintenance_Cost[g])/((
                    1+model.Discount_Rate)**yt)for (yt,ut) in model.yu_tup)for g in model.generator_types)

    OyM_Bat = sum((model.Battery_Nominal_Capacity[ut]*model.Battery_Investment_Cost*model.Battery_Operation_Maintenance_Cost)/((
                    1+model.Discount_Rate)**yt)for (yt,ut) in model.yu_tup)

    return model.Operation_Maintenance_Cost_Act == OyM_Ren + OyM_Gen + OyM_Bat

    
def Operation_Maintenance_Cost_NonAct(model):
    '''
    This funtion calculate the operation and maintenance for the system. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''    
    OyM_Ren = sum(sum((model.Renewable_Units[ut,r]*model.Renewable_Nominal_Capacity[r]*model.Renewable_Investment_Cost[r]*model.Renewable_Operation_Maintenance_Cost[r])
                for (yt,ut) in model.yu_tup)for r in model.renewable_sources)
    
    OyM_Gen = sum(sum((model.Generator_Nominal_Capacity[ut,g]*model.Generator_Investment_Cost[g]*model.Generator_Operation_Maintenance_Cost[g])
                for (yt,ut) in model.yu_tup)for g in model.generator_types)

    OyM_Bat = sum((model.Battery_Nominal_Capacity[ut]*model.Battery_Investment_Cost*model.Battery_Operation_Maintenance_Cost) 
                for (yt,ut) in model.yu_tup)

    return model.Operation_Maintenance_Cost_NonAct == OyM_Ren + OyM_Gen + OyM_Bat


def Battery_Reposition_Cost_Act(model,s):
    '''
    This funtion calculate the reposition of the battery after a stated time of use. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    
    '''
    Battery_cost_in = [0 for y in model.years]
    Battery_cost_out = [0 for y in model.years]
    Battery_Yearly_cost = [0 for y in model.years]
    
    for y in range(1,model.Years+1):
    
        Battery_cost_in[y-1] = sum(model.Energy_Battery_Flow_In[s,y,t]*model.Unitary_Battery_Reposition_Cost for t in model.periods)
        Battery_cost_out[y-1] = sum(model.Energy_Battery_Flow_Out[s,y,t]*model.Unitary_Battery_Reposition_Cost for t in model.periods)
        Battery_Yearly_cost[y-1] = Battery_cost_in[y-1] + Battery_cost_out[y-1]

    return model.Battery_Reposition_Cost_Act[s] == sum(Battery_Yearly_cost[y-1]/((1+model.Discount_Rate)**y) for y in model.years) 
    

def Battery_Reposition_Cost_NonAct(model,s):
    '''
    This funtion calculate the reposition of the battery after a stated time of use. 
    
    :param model: Pyomo model as defined in the Model_creation library.
    
    '''
    Battery_cost_in = [0 for y in model.years]
    Battery_cost_out = [0 for y in model.years]
    Battery_Yearly_cost = [0 for y in model.years]
    
    for y in range(1,model.Years+1):
    
        Battery_cost_in[y-1] = sum(model.Energy_Battery_Flow_In[s,y,t]*model.Unitary_Battery_Reposition_Cost for t in model.periods)
        Battery_cost_out[y-1] = sum(model.Energy_Battery_Flow_Out[s,y,t]*model.Unitary_Battery_Reposition_Cost for t in model.periods)
        Battery_Yearly_cost[y-1] = Battery_cost_in[y-1] + Battery_cost_out[y-1]

    return model.Battery_Reposition_Cost_NonAct[s] == sum(Battery_Yearly_cost[y-1] for y in model.years) 

    
def Scenario_Net_Present_Cost(model,s): 
    '''
    This function computes the Net Present Cost for the life time of the project, taking in account that the 
    cost are fix for each year.
    
    :param model: Pyomo model as defined in the Model_creation library.
    '''            
    foo = []
    for g in range(1,model.Generator_Types+1):
            foo.append((s,g))
            
    Fuel_Cost = sum(model.Total_Fuel_Cost_Act[s,g] for s,g in foo)
    
    return model.Scenario_Net_Present_Cost[s] == (model.Investment_Cost + model.Operation_Maintenance_Cost_Act + model.Battery_Reposition_Cost_Act[s] 
            + model.Scenario_Lost_Load_Cost_Act[s] + Fuel_Cost)   

                
def Renewable_Energy_Penetration(model,ut):
    
    upgrade_years_list = [1 for i in range(len(model.upgrades))]
    s_dur = model.Step_Duration
    for i in range(1, len(model.upgrades)): 
        upgrade_years_list[i] = upgrade_years_list[i-1] + s_dur
    yu_tuples_list = [0 for i in model.years]
    if model.Upgrades_Number == 1:
        for y in model.years:        
            yu_tuples_list[y-1] = (y, 1)
    else:    
        for y in model.years:        
            for i in range(len(upgrade_years_list)-1):
                if y >= upgrade_years_list[i] and y < upgrade_years_list[i+1]:
                    yu_tuples_list[y-1] = (y, model.upgrades[i+1])            
                elif y >= upgrade_years_list[-1]:
                    yu_tuples_list[y-1] = (y, len(model.upgrades))   
    
    years_list = []
    for i in yu_tuples_list:
        if i[1]==ut:
            years_list += [i[0]]        
    
    Foo=[]
    for s in range(1, model.Scenarios + 1):
        for y in years_list:
            for g in range(1, model.Generator_Types+1):
                for t in range(1,model.Periods+1):
                    Foo.append((s,y,g,t))    
                    
    foo=[]
    for s in range(1, model.Scenarios + 1):
        for y in years_list:
            for r in range(1, model.Renewable_Sources+1):
                for t in range(1,model.Periods+1):
                    foo.append((s,y,r,t))    
    
    E_gen = sum(model.Total_Generator_Energy[s,y,g,t]*model.Scenario_Weight[s]
                for s,y,g,t in Foo)
    
    E_ren = sum(model.Total_Renewable_Energy[s,y,r,t]*model.Scenario_Weight[s]
                for s,y,r,t in foo)
        
    return  (1 - model.Renewable_Penetration)*E_ren >= model.Renewable_Penetration*E_gen   

    
def Battery_Min_Capacity(model,ut):
    
    return   model.Battery_Nominal_Capacity[ut] >= model.Battery_Min_Capacity[ut]


def Battery_Min_Step_Capacity(model,yt,ut):
    
    if ut > 1:
        return model.Battery_Nominal_Capacity[ut] >= model.Battery_Nominal_Capacity[ut-1]
    elif ut == 1:
        return model.Battery_Nominal_Capacity[ut] == model.Battery_Nominal_Capacity[ut]
    
    
def Renewables_Min_Step_Units(model,yt,ut,r):

    if ut > 1:
        return model.Renewable_Units[ut,r] >= model.Renewable_Units[ut-1,r]
    elif ut == 1:
        return model.Renewable_Units[ut,r] == model.Renewable_Units[ut,r]
    
    
def Generator_Min_Step_Capacity(model,yt,ut,g):

    if ut > 1:
        return model.Generator_Nominal_Capacity[ut,g] >= model.Generator_Nominal_Capacity[ut-1,g]
    elif ut ==1:
        return model.Generator_Nominal_Capacity[ut,g] == model.Generator_Nominal_Capacity[ut,g]
    
    
def Investment_Cost_Limit(model):
    
    return model.Investment_Cost <= model.Investment_Cost_Limit


def Scenario_Variable_Cost_Act(model, s):
    
    foo = []
    for g in range(1,model.Generator_Types+1):
            foo.append((s,g))   
    Fuel_Cost = sum(model.Total_Fuel_Cost_Act[s,g] for s,g in foo)
    
    return model.Total_Scenario_Variable_Cost_Act[s] == model.Operation_Maintenance_Cost_Act + model.Battery_Reposition_Cost_Act[s] + model.Scenario_Lost_Load_Cost_Act[s] + Fuel_Cost


def Scenario_Variable_Cost_NonAct(model, s):
    
    foo = []
    for g in range(1,model.Generator_Types+1):
            foo.append((s,g))   
    Fuel_Cost = sum(model.Total_Fuel_Cost_NonAct[s,g] for s,g in foo)
    
    return model.Total_Scenario_Variable_Cost_NonAct[s] == model.Operation_Maintenance_Cost_NonAct + model.Battery_Reposition_Cost_NonAct[s] + model.Scenario_Lost_Load_Cost_NonAct[s] + Fuel_Cost


def Total_Variable_Cost_Obj(model):
    
    return (sum(model.Total_Scenario_Variable_Cost_NonAct[s]*model.Scenario_Weight[s] for s in model.scenarios))


def Total_Variable_Cost_Act(model):

    return model.Total_Variable_Cost_Act == (sum(model.Total_Scenario_Variable_Cost_Act[s]*model.Scenario_Weight[s] for s in model.scenarios))
