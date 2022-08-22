"""
This function is used to calculate the 3rd order cumulant fit for the selected
data in the data treeview. It applies the weighting selected in the fit options,
the expansion degree and returns the fit x,y tables to the interactive plot
script.
"""
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import math
import scipy
import scipy.optimize
import scipy.misc
import scipy.stats
import ctypes





#import of internal function and parameters
import stormsFunctions.internalSettings as internalSettings
import stormsFunctions.functionWeighting as weighting
# Import the data as an array


def residuesCumulant2ndOrder(data,fit):
    residues = []
    zip_object = zip(data,fit)
    for list1_i,list2_i in zip_object:
        residues.append(list1_i-list2_i)
    return residues

def bar(percent,progress,loading_window):
    progress['value'] = percent
    loading_window.update()


 # Boltzmann’s constant , J/K ( joules per kelvin)
def getAssociatedKey(my_dict,assocValues,item): # this function returns the associated key in the datacontainer for an item selected in the treeview
        keyFileName=[] # list to store key
        assocFileName=assocValues[item][0] # get filename of the item
        assocRecord="{}".format(assocValues[item][2]) # get record of the item
        print("assocRecord :")
        print(int(assocRecord))
        print("v1 :")
        for k1,v1 in my_dict.items(): # loop on all the keys of the datacontainer
            print(v1)
            if np.isin(int(assocRecord),v1) :  # identifies matching records
                keyFileName.append(k1) # stores matching keys for records
            elif np.isin(str(assocRecord),v1):
                keyFileName.append(k1)
        for i in keyFileName: # identifies in matching records key the matching filename and find the matching unique key
            if my_dict[i][0]==assocFileName:
                return i # return the key corresponding to the item


def fitmodel_2nd_order(t,B,beta,Gamma,mu_2):
    # T = 273.15+temp # Kelvin , roomtemp
    # eta = 10.016e-4 # viscosity of water , Pa s (pascal seconds)
    # lam = 632.8e-9 # wavelength in meters
    # theta = np.pi # scattering angle in radians
    # n = 1.33200 # refractive index
    # q = (4*np.pi*n)/(lam)*np.sin(theta/2)
    # Gamma1 = popt1 [ 2 ] # exponetial constant from 2nd order fit
    # D1 = (Gamma1 / q**2) /0.001 # Diffusion constant with conversion from ms to s
    # Gamma2 = popt2 [ 2 ] # exponetial constant from 3rd order fit
    # D2 = (Gamma2 / q**2) /0.001
    # R1 = k*T/(6*np.pi*eta*D1)
#     R unc 1 = R1 * f r a c u n c e r t a i n t i e s 1 [ 0 ]
#     print ”The hydrodynamic radius from the 2nd order f i t : ” , R1
#     print ”The unce r t a i n i ty of R i s +−” , str ( R unc 1 )
#     88
#     R2 = k*T / (6*np . pi * eta *D2)
#     R unc 2 = R2 * f r a c u n c e r t a i n t i e s 2 [ 0 ]
#     print ”The hydrodynamic radius from the 3rd order f i t : ” , R2
#     print ”The unce r t a i n i ty of R i s +−” , str ( R unc 2 )
    return B + beta*np.e**(-2*Gamma*t)*(1+(mu_2/2*t**2)**2)


def fitCumulant2ndOrder(treeViewData,treeViewFit):
    loading_window = tk.Toplevel()
    loading_window.title("")
	#loading_window.geometry("{}x{}+{}+{}".format(round(screenWidth*0.15),round(screenHeight*0.15),round(screenWidth*0.25),round(screenWidth*0.25)))

    fittingLbl = tk.Label(loading_window,text='Cumulants 2nd order fitting...')
    progress = ttk.Progressbar(loading_window, orient = tk.HORIZONTAL, length = 100, mode = 'determinate')
    fittingLbl.pack()
    progress.pack(pady=5)

    assocValues={}
    ref_dict = internalSettings.dataMainContainer
    iidDataCheckedItems=treeViewData.get_checked()
    i=0
    for item in iidDataCheckedItems:
        i+=1
        assocValues[item]=treeViewData.item(item)["values"]
        keytoFit = getAssociatedKey(internalSettings.dataMainContainer,assocValues,item)
        dataXtoFit = np.asarray(ref_dict[keytoFit][7])
        dataYtoFit = np.asarray(ref_dict[keytoFit][8])
        dataXtoFit = dataXtoFit[np.logical_not(np.isnan(dataXtoFit))]
        dataYtoFit = dataYtoFit[np.logical_not(np.isnan(dataYtoFit))]
        if len(dataYtoFit) < len(dataXtoFit):
            amount_to_remove =  len(dataXtoFit)-len(dataYtoFit)
            dataXtoFit=dataXtoFit[:-int(amount_to_remove)]

        elif (len(dataXtoFit) < len(dataYtoFit)):
            amount_to_remove = len(dataYtoFit)-len(dataXtoFit)

        else:
            pass

        #print(len(dataXtoFit),len(dataYtoFit))
        #print(dataXtoFit)
        #print(dataYtoFit)


        temp = float(internalSettings.dataMainContainer[keytoFit][3])+273.15
        print('temp={}'.format(temp))
        viscosity = float(internalSettings.dataMainContainer[keytoFit][4])*10**-3
        print('viscosity={}'.format(viscosity))
        ref_index = float(internalSettings.dataMainContainer[keytoFit][6])
        print('ref_index={}'.format(ref_index))
        angle = float(internalSettings.dataMainContainer[keytoFit][5])*np.pi/180.0
        print('angle={}'.format(angle))
        if internalSettings.dataMainContainer[keytoFit][9]=='Malvern':
            wavelength = 635.0
            #print('here')
            #print(ref_index,angle,wavelength)
        elif internalSettings.dataMainContainer[keytoFit][9]=='VascoKin':
            wavelength = 635.0
        elif internalSettings.dataMainContainer[keytoFit][9]=='Wyatt':
            wavelength = 635.0
        elif internalSettings.dataMainContainer[keytoFit][9]=='Multiangle':
            wavelength = 635.0

        q = (4*np.pi*ref_index)/(wavelength*10**-9)*np.sin(angle/2)



# Using the expansion
# gˆ2 = B + beta* eˆ{−2*Gamma\ tau }*(1 + mu 2/2! * tau ˆ2 − mu 3/3!* tau ˆ3 )
#2nd Order Cumulant Fi t

        for i in range(0,len(dataXtoFit),1):
            if dataXtoFit[i]<internalSettings.x_min_correlo:
                dataXtoFit[i]=np.NAN
                dataYtoFit[i]=np.NAN

            if dataXtoFit[i]>internalSettings.x_max_correlo:
                dataXtoFit[i]=np.NAN
                dataYtoFit[i]=np.NAN

            if dataYtoFit[i]<internalSettings.y_min_correlo:
                dataXtoFit[i]=np.NAN
                dataYtoFit[i]=np.NAN

            if dataYtoFit[i]>internalSettings.y_max_correlo:
                dataXtoFit[i]=np.NAN
                dataYtoFit[i]=np.NAN

        dataXtoFit = dataXtoFit[np.logical_not(np.isnan(dataXtoFit))]
        dataYtoFit = dataYtoFit[np.logical_not(np.isnan(dataYtoFit))]


        dataXtoFit, dataYtoFit = weighting.function_Weighting(dataXtoFit,dataYtoFit)
        try:
            popt1,pcov1 = scipy.optimize.curve_fit(fitmodel_2nd_order,dataXtoFit,dataYtoFit)

        except RuntimeError:
            ctypes.windll.user32.MessageBoxW(0, "Selection isn't wide enough to fit\nPlease select more data points", "Warning", 1)

        fitY=[]
        fitY=popt1[0]+ popt1[1]*np.e**(-2*popt1[2]*dataXtoFit)*(1+(popt1[3]/2*dataXtoFit**2)**2)
        uncertainties = np.sqrt(np.diag(pcov1))
        gamma = popt1[2]
        D = gamma/(q**2)
        k = 1.38065*10**-23
        Rh=(k*temp)/(6*np.pi*viscosity*(D))
        print('gamma={}'.format(gamma))
        print('Rh={}'.format(Rh))
        variance = popt1[3]
        PDI = popt1[3]/(popt1[2]**2)
        residues = np.array([[dataXtoFit],[residuesCumulant2ndOrder(dataYtoFit,fitY)]])
        frac_uncertainties=(uncertainties/popt1)
        std_dev_Rh = Rh*frac_uncertainties[0]
        #print(q)
        #print(gamma)
# 		poptUncertainties1 = np.sqrt(np.diag(pcov1))
# 		print(poptUncertainties1)
# 		fracUncertainties = (poptUncertainties1/popt1)
        treeViewFit.insert("","end",text="", values=(assocValues[item][0],\
                                                            assocValues[item][1],\
                                                            assocValues[item][2],\
                                                            'Cumulant 2nd order',\

                                                            assocValues[item][3],\
                                                            assocValues[item][4],\
                                                            assocValues[item][5],\
                                                            assocValues[item][6]))
        internalSettings.keyCountFits+=1
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(assocValues[item][0])
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(assocValues[item][1])
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append("{}".format(assocValues[item][2]))
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append('Cumulant 2nd order')


        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(assocValues[item][3])
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(assocValues[item][4])
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(assocValues[item][5])
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(assocValues[item][6])
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(dataXtoFit)
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(fitY)
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(q)
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(gamma)
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(D)
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(Rh)
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append((np.abs(std_dev_Rh)))
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(PDI)
        internalSettings.fitMainContainer[internalSettings.keyCountFits].append(residues)


        percent = (i*100)/len(iidDataCheckedItems)
        bar(percent,progress,loading_window)
    loading_window.destroy()



# Use these fits to solve for the hydrodynamic radius
# Data taken at a scattering angle of 90 degrees with a 632.8 nm HeNe laser .
