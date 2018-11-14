# -*- coding: utf-8 -*-
"""
@author: LR_GG
"""
import pandas as pd
import math
import matplotlib.pyplot as plt

R = 8.314  # Gas constant
g = 9.814 # Gravity acceleration [m/s^2]
T_0 = 273.15 # K
MM_air = 0.0289647 # Molecular mass of air [kg/mol]

# Import geographical, wind turbine and time-dependent parameters
Geo_params = pd.read_excel('Example/Input_Params.xlsx','Geo params')
WT_params = pd.read_excel('Example/Input_Params.xlsx','WT params')
Time_params = pd.read_excel('Example/Input_Params.xlsx','Time params')


# Definition of geographical parameters
P_0 = float(Geo_params.loc['P_0'])           # Pa
rho_0 = float(Geo_params.loc['rho_0'])       # kg/m^3
altitude = float(Geo_params.loc['altitude']) # m

# Definition of wind turbine parameters related to wind energy
radius = float(WT_params.loc['radius'])           # m
cp =0.53 # float(WT_params.loc['cp'])                   # []
eta_el = float(WT_params.loc['eta_el'])           # []
eta_gearbox = float(WT_params.loc['eta_gearbox']) # []
v_cut_in = float(WT_params.loc['v_cut_in'])       # m/s
v_cut_off = float(WT_params.loc['v_cut_off'])     # m/s
WT_rated_power = float(WT_params.loc['rated_power'])     # W

# Definition of time-dependent parameters related to wind energy
wind_speeds = Time_params[:]['wind den']         # m/s
temperatures = Time_params[:]['t den'] + T_0 # K
ninja_power_output = Time_params[:]['P denmark']

v_average = float(wind_speeds.mean())
v_rated = 13 #1.7 * v_average     #From statistics. Reference: T. Burton et alt., "Wind Energy Handbook", John Wiley & Sons, 2001

air_pressure = P_0 * math.exp(- rho_0 / P_0 * g * altitude) # Pa

area = math.pi * radius**2 # It should depend if HAWT or VAWT!!!

air_density = [[] for i in range(Time_params.shape[0])]     # kg/m^3
WT_power_output = [[] for i in range(Time_params.shape[0])] # W

a = (WT_rated_power / (v_rated**3 - v_cut_in**3))
b=  (v_rated**3 / (v_rated**3 - v_cut_in**3))


for t  in range(1,Time_params.shape[0]+1):
    
    air_density[t-1] = air_pressure / R /temperatures[t] * MM_air
    
    if wind_speeds[t] < v_cut_in:       #if v lower than v_cut_in, WT does not produce any power
        WT_power_output[t-1] = 0
        
    elif wind_speeds[t] >= v_cut_off:   #if v larger than v_cut_off WT does not produce any power
        WT_power_output[t-1] = 0
        
    elif v_rated <= wind_speeds[t] < v_cut_off:    #between v_rated and v_cut_off, power is constant
        WT_power_output[t-1] = WT_rated_power
        #WT_power_output[t-1] =  0.5 * cp * air_density[t-1] * area * v_rated**3 * eta_el * eta_gearbox
        
    else:                               #between v_cut_in and v_rated, power is variable
        WT_power_output[t-1] = a * wind_speeds[t]**3 - b * WT_rated_power 
        #WT_power_output[t-1] = 0.5 * cp * air_density[t-1] * area * wind_speeds[t]**3 * eta_el * eta_gearbox
    
    
plt.plot(WT_power_output)
plt.plot(ninja_power_output)

