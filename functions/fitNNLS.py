# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 10:26:27 2022

@author: Nelson
"""

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
from scipy.optimize import nnls

def fit_NNLS(data,rows_selected):
    print('-----------------FIT NNLS-----------------------')
    print (len(rows_selected))
    classes_N=100 #nombre de classe prédéfini pour le test
    scale_factor=1
    wavelength = 635
    boltzman = 1.380649*10**(-23)
    for i in range(0,len(rows_selected),1):
        
        exp_g = data[i]['Gamma']
        exp_g1 = exp_g*np.sign(exp_g*np.sqrt(np.abs(exp_g)))
        #print(exp_g1)
        exp_angle=np.float(data[i]['Angle (°)'])
        exp_visco=np.float(data[i]['Viscos.'])
        exp_temp=np.float(data[i]['T (°C)'])
        exp_tau = data[i]['Time']
        
        M_correlogram_length=len(exp_g1)
        #print(M_correlogram_length)
        v_min=np.min(exp_g1)
        v_max=np.max(exp_g1)
        
        for j in range(0,M_correlogram_length,1):
            if(exp_g1[j] > v_min + 0.5*(v_max-v_min)):
                  k=j
        
        v_desc=1/exp_tau[k]
        
        s = np.logspace(np.log10(v_desc/50/(10**(2*scale_factor))), np.log10(v_desc*2*(10**scale_factor)/10), classes_N);
        q = (4*np.pi*1.33)/(wavelength*10**-9)*np.sin((exp_angle)/2)
        s = q**2*boltzman*(273.15+(exp_temp)/(6*np.pi*(exp_visco)))/s
        s = s.T
        #y = exp_g.T
        t = exp_tau
        #t = t*time_correl 
        #print(s)
        print('----')
        A = np.ones((np.size(s),np.size(t)),float)#transformer en matrice unitaire
        #print(A)
        #print(np.size(A))
        #print(A)
        sm, tm = np.meshgrid(s,t)
        #print(sm)
        #print(tm)
        A=A.T*np.exp(sm*(-tm))
        #print(A)
        U,s1,V=csvd(A)
        lambda0=lagrange(U,s1,exp_g1)
        #print(lambda0)
        #print(q)
        #high_decay_rate=g_for_calc[1]*0.9 #10% of the correlogram decrease
        #low_decay_rate=g_for_calc[1]*0.1 #90% of the correlogram decrease
        #print(g_for_calc[1])
        try:
            popt1,pcov1 = scipy.optimize.curve_fit(fitmodel_2nd_order,data[i]['Time'],data[i]['Gamma'])

        except RuntimeError:
            ctypes.windll.user32.MessageBoxW(0, "Selection isn't wide enough to fit\nPlease select more data points", "Warning", 1)
        fitY=popt1[0]+ popt1[1]*np.e**(-2*popt1[2]*np.asarray(data[i]['Time']))*(1+(popt1[3]/2*np.asarray(data[i]['Time'])**2)**2)
    return (pd.DataFrame(internalSettings.fitMainContainer).T)

def csvd(A):
    #print(np.shape(A))
    m,n = np.shape(A)
    if (m>=n):
        U,sdiag,VH =np.linalg.svd(A,full_matrices=False)
        S = np.zeros((m,n))
        #print(np.shape(U))
        #print(U)
        #print(np.shape(S))
        #print(S)
        #print(np.shape(sdiag))
        #print(sdiag)
        np.fill_diagonal(S, sdiag)
        #print(np.shape(S))
        #print(S)
        V = VH.T.conj()
    else:
        V,S,UH=np.linalg.svd(A)
        S = np.zeros((m, n))
        np.fill_diagonal(S, sdiag)
        U = UH.T.conj()
        
    
    return U,S,V

def lagrange(U,s1,V):
    npoints=200
    s1=s1.T
    m,n=np.shape(U)
    #print(np.shape(U))
    p,ps=np.shape(s1)
    #print(ps)
    beta = U.T*V
    # print(np.shape(beta))
    beta2=np.linalg.norm(V)**2-np.linalg.norm(V)**2
    if ps==2:
        s1=s1[p:-1,1]/s1[p:-1,2]
        beta = beta[p:-1,1]
    # print(np.shape(beta))
    xi=beta[0:p]/s1
    #compute the L curve
    eta=np.zeros(npoints)
    rho=eta
    lambd=np.zeros(npoints+1)
    print(np.shape(s1))
    print(type(p))
    print(s1[p-1])
    lambd[npoints]=s1[p-1]
    ratio=(s1[1]/s1[p])**(1/npoints-1)
    for i in range(npoints-1,-1,1):
        lambd[i]=ratio*lambd[i+1]
    for i in range(1,npoints,1):
        f = fil_fac(s1,lambd[i])
        eta[i]=np.linalg.norm(f*xi)
        rho[i]=np.linalg.norm((1-f)*beta[1:p])
    if (m>n) and (beta2>0):
        rho=np.sqrt(rho**2+beta2)
    #compute the lagrange function
    La = rho**2+(lambd**2)*(eta**2)
    dLa=2*lambd*(eta**2)
    mindLi=np.min(dLa)
    lambd0=lambd(mindLi)
    return lambd0
        
def fil_fac(s,reg_param,method,sl,Vl):
    p,ps=np.shape(s)
    lr=np.size(reg_param)
    f=np.zeros((p,lr))
    for j in range(1,lr,1):
        if ps==1:
            f[:,j]=s**2/(s**2+reg_param[j]**2)
        else:
            f[:,j]=s[:,1]**2/(s[:,1]**2+reg_param[j]**2*s[:,2]**2)
    return f

def fitmodel_2nd_order(t,B,beta,Gamma,mu_2):
    return B + beta*np.e**(-2*Gamma*t)*(1+(mu_2/2*t**2)**2)