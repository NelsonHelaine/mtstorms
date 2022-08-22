# internalSettings.py
import collections


def init():
    global keyCount  # global variable for mainDataContainer
    global keyCountFits
    global dataMainContainer
    global fitMainContainer
    global distributionMainContainer
    global howManyIsChecked
    global howManyFitIsChecked
    global whoIsCheckedData
    global whoIsCheckedFit
    global arraytoPlot
    global arraytoPlotFit
    global columns_data
    global columns_Fit

    whoIsCheckedData = []
    whoIsCheckedFit = []
    arraytoPlot = []
    arraytoPlotFit = []
    howManyIsChecked = 0
    howManyFitIsChecked = 0
    keyCount = 0
    keyCountFits = 0
    dataMainContainer = collections.defaultdict(list)
    fitMainContainer = collections.defaultdict(list)
    #fitMainContainer['init'].append([[nan,nan,nan,nan,nan,nan,nan,nan,nan]])
    distributionMainContainer = collections.defaultdict(list)
    columns_Fit=["Sample", "Record", "Method", "Rh", "q", "D", "Time", "Fit", "Residues"]
    columns_data=["File name", "Record", "Sample", "T (°C)", "Viscos.", "Angle (°)", "RI", "Time", "Gamma"]
