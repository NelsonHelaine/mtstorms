

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

# data selection functions for malvern files


def getIndexes(df, value):
    k, l = np.where(df.values == value)
    return k[0], l[0]


def getIndexesMultColCorrelData(df):
    arrayCorrelData = []
    arrayCorrelData = df.iloc[0].str.contains("Correlation Data", regex=False)
    idxarrayCorrelData = [idx for idx, element in enumerate(arrayCorrelData) if element == True]
    return idxarrayCorrelData


def getIndexesMultColCorrelDelayTimes(df):
    arrayCorrelDelayTimes = []
    arrayCorrelDelayTimes = df.iloc[0].str.contains("Correlation Delay", regex=False)
    idxarrayCorrelDelayTimes = [idx for idx, element in enumerate(arrayCorrelDelayTimes) if element == True]
    return idxarrayCorrelDelayTimes


def getIndexesMultColSizes(df):
    arraySizes = []
    arraySizes = df.iloc[0].str.contains("Sizes", regex=False)
    idxarraySizes = [idx for idx, element in enumerate(arraySizes) if element == True]
    return idxarraySizes


def getIndexesMultColIntensities(df):
    arrayIntensities = []
    arrayIntensities = df.iloc[0].str.contains("Intensities", regex=False)
    idxarrayIntensities = [idx for idx, element in enumerate(arrayIntensities) if element == True]
    return idxarrayIntensities


def getIndexesMultColNumbers(df):
    arrayNumbers = []
    arrayNumbers = df.iloc[0].str.contains("Numbers", regex=False)
    idxarrayNumbers = [idx for idx, element in enumerate(arrayNumbers) if element == True]
    return idxarrayNumbers


def getIndexesMultColSizePeak(df):
    arraySizePeak = []
    arraySizePeak = df.iloc[0].str.contains("Size Peak", regex=False)
    idxarraySizePeak = [idx for idx, element in enumerate(arraySizePeak) if element == True]
    return idxarraySizePeak


def getIndexesMultColPeakArea(df):
    arrayPeakArea = []
    arrayPeakArea = df.iloc[0].str.contains("Peak Area", regex=False)
    idxarrayPeakArea = [idx for idx, element in enumerate(arrayPeakArea) if element == True]
    return idxarrayPeakArea


# main datafile import function


def openDataFile(contents, filename, date):

    content_type, content_string = contents.split(",")
    # content_string.encode('utf-8').strip()
    decoded = base64.b64decode(content_string)
    # print(decoded)
    global fileType
    fileType=""
    #importedData=[]
#for i in range(0,len(filename)): #loop on all the files selected
    if fnmatch.fnmatch(filename, "*.txt"):  # if its a txt, its a malvern or vascokin file
        print(filename)
        try:
            try:  # import with pandas package and avoiding parse errors
                df_data = pd.read_csv(
                    io.StringIO(decoded.decode("utf-8")), header=None, sep="\t"
                )  # for malvern and vascokin files separator is tab

            except pd.errors.ParserError as err:
                str_find = "saw"
                int_position = int(str(err).find(str_find)) + len(str_find)
                str_nbCol = str(err)[int_position:]
                l_col = range(int(str_nbCol))
                print('h1')
                df_data = pd.read_csv(
                        io.StringIO(decoded.decode("utf-8")), header=None, sep="\t",names=l_col)
        except:
            try:  # import with pandas package and avoiding parse errors
                df_data = pd.read_csv(
                    io.StringIO(decoded.decode("latin1")), header=None, sep="\t"
                )
            except pd.errors.ParserError as err:
                str_find = "saw "
                int_position = int(str(err).find(str_find)) + len(str_find)
                str_nbCol = str(err)[int_position:]
                l_col = range(int(str_nbCol))
                print('h2')
                df_data = pd.read_csv(
                        io.StringIO(decoded.decode("latin1")), header=None, sep="\t",names=l_col)



        if df_data.iloc[0, 0] == "Record":  # pattern for malvern files
            fileType="malvern"
            print(fileType)
            df_data = df_data.replace(",", ".", regex=True)  # replace , by . in order to avoid storage problems
            # import of all the specs indexes to access them easily in the structure
            idxSampleNameMalv = getIndexes(df_data, "Sample Name")
            idxRecordMalv = getIndexes(df_data, "Record")
            idxTypeMalv = getIndexes(df_data, "Type")
            idxMeasurementDateMalv = getIndexes(df_data, "Measurement Date and Time")
            idxTempMalv = getIndexes(df_data, "T (°C)")
            idxDerivCountRatesMalv = getIndexes(df_data, "Derived Count Rate (kcps)")
            idxZaveMalv = getIndexes(df_data, "Z-Ave (d.nm)")
            idxIntensityMeanMalv = getIndexes(df_data, "Intensity Mean (d.nm)")
            idxNumberMeanMalv = getIndexes(df_data, "Number Mean (d.nm)")
            idxPdIMalv = getIndexes(df_data, "PdI")
            idxAttenuatorMalv = getIndexes(df_data, "Attenuator")
            idxCorrelDataMalv = getIndexesMultColCorrelData(df_data)
            idxCorrelDelayTimesMalv = getIndexesMultColCorrelDelayTimes(df_data)
            idxSizesMalv = getIndexesMultColSizes(df_data)
            idxIntensitiesMalv = getIndexesMultColIntensities(df_data)
            idxNumbersMalv = getIndexesMultColNumbers(df_data)
            idxSizePeakMalv = getIndexesMultColSizePeak(df_data)
            idxPeakArea = getIndexesMultColPeakArea(df_data)
            idxScatAngleMalv = getIndexes(df_data, "Scattering Angle (°)")
            idxViscosityMalv = getIndexes(df_data, "Viscosity (cP)")
            idxDispersantRMalv = getIndexes(df_data, "Dispersant RI")
            idxAppliedRegulariserMalv = getIndexes(df_data, "Applied Regulariser")
            for j in range(1, len(df_data)):  # loop on all the experiments of the files
                # adding the different specs to checkboxtreeview widget

                # adding the data to the main data container
                internalSettings.keyCount += 1
                internalSettings.dataMainContainer[internalSettings.keyCount].append(os.path.basename(filename))
                internalSettings.dataMainContainer[internalSettings.keyCount].append(df_data.iloc[j, idxRecordMalv[1]])
                internalSettings.dataMainContainer[internalSettings.keyCount].append(
                    df_data.iloc[j, idxSampleNameMalv[1]]
                )
                internalSettings.dataMainContainer[internalSettings.keyCount].append(df_data.iloc[j, idxTempMalv[1]])
                internalSettings.dataMainContainer[internalSettings.keyCount].append(
                    df_data.iloc[j, idxViscosityMalv[1]]
                )
                internalSettings.dataMainContainer[internalSettings.keyCount].append(
                    df_data.iloc[j, idxScatAngleMalv[1]]
                )
                internalSettings.dataMainContainer[internalSettings.keyCount].append(
                    df_data.iloc[j, idxDispersantRMalv[1]]
                )
                internalSettings.dataMainContainer[internalSettings.keyCount].append(
                    pd.to_numeric(df_data.iloc[j, idxCorrelDelayTimesMalv]).to_numpy()
                )
                internalSettings.dataMainContainer[internalSettings.keyCount].append(
                    pd.to_numeric(df_data.iloc[j, idxCorrelDataMalv]).to_numpy()
                )

        if (
            df_data.iloc[0, 0] == "Name"
        ):  # for Vascokin files, params values are on the same line than the names, following column
            fileType="vasco"
            print(fileType)
            #print(df_data)
            df_data = df_data.replace(",", ".", regex=True)  # replace , by . in order to avoid storage problems
            idxSampleNameVasco = tuple(np.add(getIndexes(df_data, "Name"), (0, 1)))
            idxTempVasco = tuple(np.add(getIndexes(df_data, "Temperature (°C)"), (0, 1)))
            idxOperatorVasco = tuple(np.add(getIndexes(df_data, "by"), (0, 1)))
            idxSolventVasco = tuple(np.add(getIndexes(df_data, "Solvent"), (0, 1)))
            idxRefIndexVasco = tuple(np.add(getIndexes(df_data, "Refractive index "), (0, 1)))
            idxRealPartVasco = tuple(np.add(getIndexes(df_data, "Real part (a.u) "), (0, 1)))
            idxImPartVasco = tuple(np.add(getIndexes(df_data, "Imaginary part (a.u) "), (0, 1)))
            # idxTauVasco = tuple(np.add(getIndexes(df_data, 'Tau (µs)'),(0,1)))
            idxNbChannelsVasco = tuple(np.add(getIndexes(df_data, "Number of channels"), (0, 1)))
            idxLaserPowerVasco = tuple(np.add(getIndexes(df_data, "Laser power (%)"), (0, 1)))
            idxWavelengthVasco = tuple(np.add(getIndexes(df_data, "Wavelength (nm)"), (0, 1)))
            idxAngleVasco = tuple(np.add(getIndexes(df_data, "Angle (°)"), (0, 1)))
            #idxHeadVasco = np.add(getIndexes(df_data, "Head"), (0, 1))
            idxMeasurementDateVasco = tuple(np.add(getIndexes(df_data, "Measurement Date (DD/MM/YY HH:mm)"), (0, 1)))
            idxExtractDateVasco = tuple(np.add(getIndexes(df_data, "Extract Date (DD/MM/YY HH:mm)"), (0, 1)))
            idxDurationVasco = tuple(np.add(getIndexes(df_data, "Duration (s)"), (0, 1)))
            idxRawDataVasco = tuple(np.add(getIndexes(df_data, "Raw Data"), (0, 0)))
            idxCorrelogramVasco = tuple(np.add(getIndexes(df_data, "Correlogram"), (0, 1)))
            idxCumulantsNameVasco = getIndexes(df_data, "Cumulants")
            idxViscosityVasco = tuple(np.add(getIndexes(df_data, "Viscosity(cP)"), (0, 1)))
            # print(idxCumulantsNameVasco)

            idxStartDataTimeVasco = tuple(np.add(idxRawDataVasco, (2, 0)))
            idxEndDataTimeVasco = tuple(np.subtract(idxCumulantsNameVasco, (1, 0)))
            idxsYDataTime = np.arange(start=idxStartDataTimeVasco[0], stop=idxEndDataTimeVasco[0], step=1)
            idxsXDataTime = np.empty(len(idxsYDataTime))
            idxsXDataTime.fill(int(idxStartDataTimeVasco[1]))
            idxsDataTime = np.vstack([idxsYDataTime, idxsXDataTime])

            idxStartDataCorrelVasco = tuple(np.add(idxCorrelogramVasco, (1, 0)))
            idxEndDataCorrelVasco = tuple(np.subtract(idxCumulantsNameVasco, (1, 0)))
            idxsYDataCorrel = np.arange(start=idxStartDataCorrelVasco[0], stop=idxEndDataCorrelVasco[0], step=1)
            idxsXDataCorrel = np.empty(len(idxsYDataCorrel))
            idxsXDataCorrel.fill(int(idxStartDataCorrelVasco[1]))
            idxsDataCorrel = np.vstack([idxsYDataCorrel, idxsXDataCorrel])

            internalSettings.keyCount += 1
            internalSettings.dataMainContainer[internalSettings.keyCount].append(os.path.basename(filename))
            internalSettings.dataMainContainer[internalSettings.keyCount].append(1)
            internalSettings.dataMainContainer[internalSettings.keyCount].append(df_data.iloc[idxSampleNameVasco])
            internalSettings.dataMainContainer[internalSettings.keyCount].append(df_data.iloc[idxTempVasco])
            internalSettings.dataMainContainer[internalSettings.keyCount].append(df_data.iloc[idxViscosityVasco])
            internalSettings.dataMainContainer[internalSettings.keyCount].append(df_data.iloc[idxAngleVasco])
            internalSettings.dataMainContainer[internalSettings.keyCount].append(df_data.iloc[idxRealPartVasco])

            internalSettings.dataMainContainer[internalSettings.keyCount].append(
                pd.to_numeric(df_data.iloc[idxsDataTime[0][:], 0]).to_numpy()
            )
            internalSettings.dataMainContainer[internalSettings.keyCount].append(
                pd.to_numeric(df_data.iloc[idxsDataCorrel[0][:], 1]).to_numpy()
            )
            #print("data main container contents:")
            #print(internalSettings.dataMainContainer)


    if fnmatch.fnmatch(filename, "*.csv"):
        try:
            df_data = pd.read_csv(filename, header=None, sep=",")
        except pd.errors.ParserError as err:
            str_find = "saw "
            int_position = int(str(err).find(str_find)) + len(str_find)
            str_nbCol = str(err)[int_position:]
            l_col = range(int(str_nbCol))
            df_data = pd.read_csv(filename, header=None, sep=",", names=l_col)

        internalSettings.keyCount += 1
        internalSettings.dataMainContainer[internalSettings.keyCount].append(os.path.basename(filename))
        internalSettings.dataMainContainer[internalSettings.keyCount].append(i + 1)
        internalSettings.dataMainContainer[internalSettings.keyCount].append("")
        internalSettings.dataMainContainer[internalSettings.keyCount].append("")
        internalSettings.dataMainContainer[internalSettings.keyCount].append("")
        internalSettings.dataMainContainer[internalSettings.keyCount].append("")
        internalSettings.dataMainContainer[internalSettings.keyCount].append("")
        internalSettings.dataMainContainer[internalSettings.keyCount].append(
            pd.to_numeric(df_data.iloc[1:-1][0]).to_numpy()
        )
        internalSettings.dataMainContainer[internalSettings.keyCount].append(
            pd.to_numeric(df_data.iloc[1:-1][1]).to_numpy()
        )

    if fnmatch.fnmatch(filename, "*.dat"):  # for multi angle files
        fileType=='wyatt'
        print('here')
        try:
            df_data = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")),
                header=None,
                sep="\t",
                decimal=".",
                names=["0", "1", "2"],
                engine="python",
                error_bad_lines=False,
            )
            print(df_data.iloc[2,0])
        except pd.errors.ParserError as err:
            str_find = "saw "
            int_position = int(str(err).find(str_find)) + len(str_find)
            str_nbCol = str(err)[int_position:]
            l_col = range(int(str_nbCol))
            df_data = pd.read_csv(
                filename,
                header=None,
                sep="\t",
                decimal=".",
                names=["0", "1", "2"],
                engine="python",
                error_bad_lines=False,
            )
        #print(df_data)

        if (
            df_data.iloc[2, 0] == "Scattering angle:"
        ):  # for multi angle files, params values are on the same line than the names, following column

            print('here2')
            df_data = df_data.replace(",", ".", regex=True)  # replace , by . in order to avoid storage problems
            #print(df_data)
            idxSampleNameMulti = (0, 1)
            idxTempMulti = tuple(np.add(getIndexes(df_data, "Temperature (K):"), (0, 1)))

            idxRefIndexMulti = tuple(np.add(getIndexes(df_data, "Refractive index:"), (0, 1)))
            idxLaserPowerMulti = tuple(np.add(getIndexes(df_data, "Laser intensity (mW):"), (0, 1)))
            idxWavelengthMulti = tuple(np.add(getIndexes(df_data, "Wavelength (nm):"), (0, 1)))
            idxAngleMulti = tuple(np.add(getIndexes(df_data, "Scattering angle:"), (0, 1)))
            idxDurationVasco = tuple(np.add(getIndexes(df_data, "Duration (s):"), (0, 1)))
            idxLagTimeMulti = tuple(np.add(getIndexes(df_data, "Lag time (s)         g2-1"), (0, 0)))
            idxCorrelMulti = tuple(np.add(getIndexes(df_data, "Lag time (s)         g2-1"), (0, 1)))
            idxCountRateMulti = getIndexes(df_data, "Count Rate History (KHz)  CR CHA / CR CHB")
            idxViscosityMulti = tuple(np.add(getIndexes(df_data, "Viscosity (mPas):"), (0, 1)))
            # print(idxCumulantsNameVasco)
            print('Here3')
            idxStartDataTimeMulti = tuple(np.add(idxLagTimeMulti, (1, 0)))
            idxEndDataTimeMulti = tuple(np.subtract(idxCountRateMulti, (1, 0)))
            idxsYDataTime = np.arange(start=idxStartDataTimeMulti[0], stop=idxEndDataTimeMulti[0], step=1)
            idxsXDataTime = np.empty(len(idxsYDataTime))
            idxsXDataTime.fill(int(idxStartDataTimeMulti[1]))
            idxsDataTime = np.vstack([idxsYDataTime, idxsXDataTime])

            idxStartDataCorrelMulti = tuple(np.add(idxCorrelMulti, (1, 0)))
            idxEndDataCorrelMulti = tuple(np.subtract(idxCountRateMulti, (1, 0)))
            idxsYDataCorrel = np.arange(start=idxStartDataCorrelMulti[0], stop=idxEndDataCorrelMulti[0], step=1)
            idxsXDataCorrel = np.empty(len(idxsYDataCorrel))
            idxsXDataCorrel.fill(int(idxStartDataCorrelMulti[1]))
            idxsDataCorrel = np.vstack([idxsYDataCorrel, idxsXDataCorrel])

            internalSettings.keyCount += 1
            internalSettings.dataMainContainer[internalSettings.keyCount].append(os.path.basename(filename))
            internalSettings.dataMainContainer[internalSettings.keyCount].append("{}".format(1))
            internalSettings.dataMainContainer[internalSettings.keyCount].append(1)
            internalSettings.dataMainContainer[internalSettings.keyCount].append(
                float(df_data.iloc[idxTempMulti]) - 273.15
            )
            internalSettings.dataMainContainer[internalSettings.keyCount].append(df_data.iloc[idxViscosityMulti])
            internalSettings.dataMainContainer[internalSettings.keyCount].append(df_data.iloc[idxAngleMulti])
            internalSettings.dataMainContainer[internalSettings.keyCount].append(df_data.iloc[idxRefIndexMulti])

            internalSettings.dataMainContainer[internalSettings.keyCount].append(
                pd.to_numeric(df_data.iloc[idxsDataTime[0][:], 0]).to_numpy()
            )
            internalSettings.dataMainContainer[internalSettings.keyCount].append(
                pd.to_numeric(df_data.iloc[idxsDataCorrel[0][:], 1]).to_numpy()
            )

    return(pd.DataFrame(internalSettings.dataMainContainer).T)
    # #print(df_data)
    # if (fileType=='malvern'):
    #     #print("malvern data main container contents:")
    #     print(pd.DataFrame(internalSettings.dataMainContainer).T)
    #     return(pd.DataFrame(internalSettings.dataMainContainer).T)
    #     #return pd.DataFrame(internalSettings.dataMainContainer[internalSettings.keyCount]).T
    #
    # else:
    #     pass
    # if (fileType=="vasco"):
    #     #print("data main container contents:")
    #     #print(pd.DataFrame(internalSettings.dataMainContainer).T)
    #     #print("vasco data main container contents:")
    #     print(pd.DataFrame(internalSettings.dataMainContainer).T)
    #     return(pd.DataFrame(internalSettings.dataMainContainer).T)
    #     #return(pd.DataFrame(internalSettings.dataMainContainer[internalSettings.keyCount]).T)
    # else:
    #     pass
    #
    # if (fileType=="wyatt"):
    #     #print("data main container contents:")
    #     #print(pd.DataFrame(internalSettings.dataMainContainer))
    #     #print("wyatt data main container contents:")
    #     print(pd.DataFrame(internalSettings.dataMainContainer).T)
    #     #return(pd.DataFrame(internalSettings.dataMainContainer).T)
    #     return(pd.DataFrame(internalSettings.dataMainContainer).T)
    # else:
    #     pass
