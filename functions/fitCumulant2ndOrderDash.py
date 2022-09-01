import base64
import datetime
import io
import dash
from dash import html
from dash import dcc
from dash import dash_table
import pandas as pd
import fnmatch
import numpy as np
import re
import collections
import functions.internalSettingsWeb as internalSettings
import os
import scipy
import scipy.optimize
import scipy.misc
import scipy.stats
import ctypes
from collections import defaultdict



def fit(data,rows_selected):
    print('----------------------------------------')
    print (rows_selected)
    wavelength = 635.0
    fitDicttoAdd=defaultdict(list)
    for i in rows_selected:
        print(data[i]['File name'])
        if data[i]['File name']=='Malvern':
            wavelength = 635.0
        elif data[i]['File name']=='VascoKin':
            wavelength = 635.0
        elif data[i]['File name']=='Wyatt':
            wavelength = 635.0
        elif data[i]['File name']=='Multiangle':
            wavelength = 635.0
        try:
            popt1,pcov1 = scipy.optimize.curve_fit(fitmodel_2nd_order,data[i]['Time'],data[i]['Gamma'])

        except RuntimeError:
            ctypes.windll.user32.MessageBoxW(0, "Selection isn't wide enough to fit\nPlease select more data points", "Warning", 1)
        print(wavelength)
        q = (4*np.pi*1.33)/(wavelength*10**-9)*np.sin(np.asarray(np.float(data[i]['Angle (°)']))/2)
        fitY=[]
        print(data[i]['Gamma'])
        fitY=popt1[0]+ popt1[1]*np.e**(-2*popt1[2]*np.asarray(data[i]['Time']))*(1+(popt1[3]/2*np.asarray(data[i]['Time'])**2)**2)
        uncertainties = np.sqrt(np.diag(pcov1))
        gamma = popt1[2]
        #print('q=')
        #print(q)
        D = gamma/(q**2)
        k = 1.38065*10**-23
        Rh=(k*np.asarray(np.float(data[i]['T (°C)'])))/(6*np.pi*np.asarray(np.float(data[i]['Viscos.']))*(D))
        #print('gamma={}'.format(gamma))
        #print('Rh={}'.format(Rh))
        variance = popt1[3]
        #print(type(variance))
        PDI = popt1[3]/(popt1[2]**2)
        residues = np.asarray(data[i]['Gamma'])-fitY
        limit_borne_inf = 1
        limit_borne_sup= 100000
        x_dist = range(limit_borne_inf,limit_borne_sup,1)
        #print(type(gamma))
        #print(type(x_dist))
        s_variance=np.sqrt(variance)
        distribution = 1/np.sqrt(2*3.1415*variance)*np.exp(-((x_dist-gamma)**2/2*variance))
        print('Dist : {}'.format(distribution))
        internalSettings.keyCountFits+=1
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(data[i]['Sample'])
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(data[i]['Record'])
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append("Cumul. 2nd ord.")
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(Rh)
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(q)
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(D)
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(np.asarray(data[i]['Time']))
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(np.asarray(fitY))
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(residues)
        #internalSettings.distributionMainContainer[internalSettings.keyCountFits].append(variance)
        internalSettings.distributionMainContainer[internalSettings.keyCountFits].append(distribution)
        print(internalSettings.distributionMainContainer)

        #print(fitDicttoAdd)
        frac_uncertainties=(uncertainties/popt1)
        std_dev_Rh = Rh*frac_uncertainties[0]
    print(internalSettings.fitMainContainer)
    print(pd.DataFrame(internalSettings.fitMainContainer).T)
    return (pd.DataFrame(internalSettings.fitMainContainer).T)

def fitmodel_2nd_order(t,B,beta,Gamma,mu_2):
    return B + beta*np.e**(-2*Gamma*t)*(1+(mu_2/2*t**2)**2)
