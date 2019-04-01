# -*- coding: utf-8 -*-
"""
@author: LR_GG
"""
import pandas as pd
import math
import matplotlib.pyplot as plt
import re
from scipy.interpolate import interp1d


def Renewable_Outputs():
    
    # Import delta time from data.dat
    Data_file = "Inputs/data.dat"
    Data_import = open(Data_file).readlines()
    delta_time = float((re.findall('\d+',Data_import[10])[0]))
    
    R = 8.314  # Gas constant
    g = 9.814 # Gravity acceleration [m/s^2]
    T_0 = 273.15 # K
    MM_air = 0.0289647 # Molecular mass of air [kg/mol]
    
    # Import geographical, wind turbine and time-dependent parameters
    Geo_params = pd.read_excel('Inputs/Input_Params.xlsx','Geo params')
    Ren_types = pd.read_excel('Inputs/Input_Params.xlsx','Ren types')
    WT_params = pd.read_excel('Inputs/Input_Params.xlsx','WT params')
    PV_params = pd.read_excel('Inputs/Input_Params.xlsx','PV params')
    PV_params = PV_params.fillna(0)
    Time_params = pd.read_excel('Inputs/Input_Params.xlsx','Time params')   

    temperatures = Time_params[:]['Temperature °C'] + T_0    # K
    temperatures.name = 'Temperatures K'
    
    if Ren_types['values']['n_WT_types'] > 0:
    
        # Definition of geographical parameters
        P_0 = Geo_params['values']['P_0']                 # Pa
        rho_0 = Geo_params['values']['rho_0']             # kg/m^3
        altitude = Geo_params['values']['altitude']       # m
        
        # Definition of parameters related to wind energy       
        wind_speeds = Time_params[:]['Wind Speed m/s']                  # m/s
        air_pressure = P_0 * math.exp(- rho_0 / P_0 * g * altitude) # Pa
        air_density = [air_pressure / R /temperatures[t] * MM_air for t in range(1, Time_params.shape[0] + 1)]     # kg/m^3
        
        # Creation of dataframe to store each turbine's energy output       
        WT_energy_output_1 = pd.DataFrame()  # W
        WT_energy_output_2 = pd.DataFrame()
        WT_energy_output_3 = pd.DataFrame() 
        WT_energy_output_4 = pd.DataFrame()
        
        for wt in range(1, Ren_types['values']['n_WT_types'] + 1):
        
            # Parameters of the WT
            radius = float(WT_params.loc['radius', wt])              # m
            cp = float(WT_params.loc['cp', wt])                      # []
            eta_el = float(WT_params.loc['eta_el', wt])              # []
            eta_gearbox = float(WT_params.loc['eta_gearbox', wt])    # []
            v_cut_in = float(WT_params.loc['v_cut_in', wt])          # m/s
            v_cut_off = float(WT_params.loc['v_cut_off', wt])        # m/s
            WT_rated_power = float(WT_params.loc['rated_power', wt]) # W
            area = math.pi * (radius**2) # It should depend if HAWT or VAWT!!!
            v_rated = float(WT_params.loc['v_rated', wt])  #1.7 * v_average  #From statistics. Reference: T. Burton et alt., "Wind Energy Handbook", John Wiley & Sons, 2001
            power_curve_available = WT_params.loc['power_curve_available', wt] # can be 'yes' or 'no'. if yes, the available plot points must be inserted in the sheet 'WT power curve'          
            
            # Parameters for wind power calculation
#            Cubic 
            ac = (WT_rated_power / (v_rated**3 - v_cut_in**3))
            bc =  (v_cut_in**3 / (v_rated**3 - v_cut_in**3))

#            Interpolated
            WT_curve = pd.read_excel('Inputs/Input_Params.xlsx','WT power curve')
            interp_curve = interp1d(WT_curve.index, WT_curve['power output [W]'], kind='cubic')            

#            Weibull (Rayleigh: c = 2)
            k = 2
            a = WT_rated_power * (v_cut_in**k) / (v_cut_in**k - v_rated**k)
            b = WT_rated_power / (- v_cut_in**k + v_rated**k)
                       
            for t  in range(1, Time_params.shape[0] + 1):
                                
                if wind_speeds[t] < v_cut_in:       #if v lower than v_cut_in, WT does not produce any power
                    WT_energy_output_1.loc[t, wt] = 0
                    WT_energy_output_2.loc[t, wt] = 0
                    WT_energy_output_3.loc[t, wt] = 0
                    WT_energy_output_4.loc[t, wt] = 0    
                    
                elif wind_speeds[t] >= v_cut_off:   #if v larger than v_cut_off WT does not produce any power
                    WT_energy_output_1.loc[t, wt] = 0
                    WT_energy_output_2.loc[t, wt] = 0
                    WT_energy_output_3.loc[t, wt] = 0
                    WT_energy_output_4.loc[t, wt] = 0
                    
                elif v_rated <= wind_speeds[t] < v_cut_off:    #between v_rated and v_cut_off, power is constant
#                    WT_energy_output_1.loc[t, wt] = WT_rated_power*delta_time
#                    WT_energy_output_2.loc[t, wt] = WT_rated_power*delta_time
#                    WT_energy_output_3.loc[t, wt] = WT_rated_power*delta_time
                    WT_energy_output_4.loc[t, wt] = WT_rated_power*delta_time
                    
                else:                               #between v_cut_in and v_rated, power is variable

                    if power_curve_available == 'yes':
                        WT_energy_output_4.loc[t, wt] = interp_curve(wind_speeds[t])

                    else:
    #                   Weibull
    #                    WT_energy_output_1.loc[t, wt] = (a + b*wind_speeds[t]**k)*delta_time
    
    #                   Physical
    #                    WT_energy_output_2.loc[t, wt] = (0.5 * cp * air_density[t-1] * area * wind_speeds[t]**3 * eta_el * eta_gearbox)*delta_time
    
    #                   Quadratic
    #                    WT_energy_output_3.loc[t, wt] = (WT_rated_power * ((wind_speeds[t]-v_cut_in)/(v_rated - v_cut_in))**2 )*delta_time   
    
    #                   Cubic
                        WT_energy_output_4.loc[t, wt] = (ac * wind_speeds[t]**3 - bc * WT_rated_power)*delta_time
                    

#        plt.plot(wind_speeds, WT_energy_output_1)
#        plt.plot(wind_speeds, WT_energy_output_2)
#        plt.plot(wind_speeds, WT_energy_output_3)        
        plt.plot(wind_speeds, WT_energy_output_4)
        legend_list = ['Cubic']
        plt.legend(legend_list)
        
    if Ren_types['values']['n_PV_types'] > 0:

        DNI = Time_params[:]['DNI W/m2']     # W/m^2
        DI = Time_params[:]['DI W/m2']       # W/m^2
        
        PV_energy_output = pd.DataFrame()  # W
        
        for pv in range(1, Ren_types['values']['n_PV_types'] + 1):
            
            # Parameters of the PV
            I_mp = float(PV_params.loc['I_mp', pv])              # A
            V_mp = float(PV_params.loc['V_mp', pv])              # V
            n_cells = float(PV_params.loc['n_cells', pv])        # []
            P_panel = float(PV_params.loc['P_panel', pv])        # W
            
            if P_panel == 0:            
                P_panel = I_mp * V_mp * n_cells                  # W 
        
            beta = float(PV_params.loc['tilt_angle', pv])        # deg
            theta = float(PV_params.loc['incidence_angle', pv])  # deg
            G_NOCT = float(PV_params.loc['G_NOCT', pv])          # W/m^2
            T_NOCT = float(PV_params.loc['T_NOCT', pv])          # °C
            T_0_NOCT = float(PV_params.loc['T_0_NOCT', pv])      # °C
            gamma = float(PV_params.loc['gamma', pv])            # % / °C
            G_STC = float(PV_params.loc['G_STC', pv])            # W/m^2
            
            for t  in range(1, Time_params.shape[0] + 1):
                
                G = DNI[t] * math.cos(math.radians(theta)) + DI[t] * (1 + math.cos(math.radians(beta))) / 2
                        
                T_cell = temperatures[t] + G/G_NOCT * (T_NOCT - T_0_NOCT)
                
                PV_energy_output.loc[t, pv] = (P_panel * G/G_STC * (1 - gamma*(T_cell - temperatures[t])))*delta_time
        
                if PV_energy_output.loc[t, pv] > P_panel:
                    PV_energy_output.loc[t, pv] = P_panel
        
        plt.figure()
        plt.plot(PV_energy_output)
    
    #Exporting the results to excel file that can be called by Micro-Grids    
    Renewable_Output_DF = pd.concat([PV_energy_output, WT_energy_output_4], axis = 1)
    columns_names = [i for i in range(1,Renewable_Output_DF.shape[1] + 1)]
    Renewable_Output_DF.columns = columns_names
    Renewable_Output_DF.to_excel('Inputs/Renewable_Energy.xls')
    
    print('Import_Inputs: Renewable_Energy.xls created')
    
    return Renewable_Output_DF