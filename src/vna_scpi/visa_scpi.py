#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import visa
import threading
import numpy as np


class Vna_measure(threading.Thread):
    def __init__(self, address, test_type = 0, chart_numbers = 0):
        threading.Thread.__init__(self)
        print("Init. visa setup")

        self.instrument_address = address
        self.test_type = test_type
        self.chart_numbers = chart_numbers

        self.instrument_info = ''
        self.data_ready = False

        self.measures = []
        self.s_parameters = []

        #start thread
        self.start()

    def run(self):
        # TEST is used for debug
        if self.instrument_address == "TEST":
            self.test_mode = True
        else:
            self.test_mode = False

            rm = visa.ResourceManager()
            self.vna = rm.open_resource(self.instrument_address)
            # Some instruments require that at the end of each command.
            self.vna.write_termination = '\n'

        #read instrument info
        try:
            self.instrument_info = self.instrumentInfo()
        except Exception as e:
            print(e)
            self.instrument_info = 'NO CONNECTION \n'

        print(self.instrument_info)

        #tmp code
        self.s_parameters = []

        for index in range(self.chart_numbers):
            if self.test_mode == True:
                x = np.linspace(1, 301)
                y = np.sin(x) + np.random.normal(scale=0.1, size = len(x))
                data = x, y

            elif self.test_type == 0:
                data = self.flanges(index)

            elif self.test_type == 1:
                data = self.pick_up(index)

            else:
                print("exception")

            self.measures.append(data)

        self.data_ready = True
        print('end measures')


#==============================================================================#
    def instrumentInfo(self):
        if self.test_mode == True:
            name = 'TEST MODE ON \n'
        else:
            name = self.vna.query('*IDN?')  # Query the Identification string
        time.sleep(1)
        return name


#==============================================================================#
    # for flange tests
    def flanges(self, index):
        #self.vna.write('*RST') # Reset the instrument
        #self.vna.write('*CLS') # Clear the Error queue

        # Display update ON - switch OFF after debugging
        self.vna.write('SYST:DISP:UPD ON')

        # -----------------------------------------------------------
        if index == 0:
            self.vna.write("CALC1:PAR:DEF 'Trc1', S21")
            self.vna.write('DISP:WIND:STAT ON')
            self.vna.write("DISP:WIND:TRAC1:FEED 'Trc1'")

            # marker
            self.vna.write('CALC1:MARK ON')
            self.vna.write('CALCulate1:MARKer1:X 2Ghz')
            self.vna.write('CALC1:FORM GDELay')
            time.sleep(1)
            self.vna.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')
            time.sleep(1)

        # -----------------------------------------------------------
        elif index == 1:
            self.vna.write("CALC1:PAR:DEF 'Trc1', S21")
            self.vna.write('DISP:WIND:STAT ON')
            self.vna.write("DISP:WIND:TRAC1:FEED 'Trc1'")
            # marker
            self.vna.write('CALC1:MARK ON')
            self.vna.write('CALCulate1:MARKer1:X 2Ghz')
            self.vna.write('CALC1:FORM MLOG')
            time.sleep(1)
            self.vna.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')
            time.sleep(1)

        # -----------------------------------------------------------
        elif index == 2:
            self.vna.write("CALC1:PAR:DEF 'Trc1', S11")
            self.vna.write('DISP:WIND:STAT ON')
            self.vna.write("DISP:WIND:TRAC1:FEED 'Trc1'")
            # marker
            self.vna.write('CALC1:MARK ON')
            self.vna.write('CALCulate1:MARKer1:X 2Ghz')
            self.vna.write('CALC1:FORM SWR')
            time.sleep(1)
            self.vna.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')
            time.sleep(1)

        # -----------------------------------------------------------
        elif index == 3:
            self.vna.write("CALC1:PAR:DEF 'Trc1', S22")
            self.vna.write('DISP:WIND:STAT ON')
            self.vna.write("DISP:WIND:TRAC1:FEED 'Trc1'")
            # marker
            self.vna.write('CALC1:MARK ON')
            self.vna.write('CALCulate1:MARKer1:X 2Ghz')
            self.vna.write('CALC1:FORM SWR')
            time.sleep(1)
            self.vna.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')
            time.sleep(1)

        # -----------------------------------------------------------
        elif index == 4:
            self.vna.write("CALC1:PAR:DEF 'Trc1', S11")
            self.vna.write('DISP:WIND:STAT ON')
            self.vna.write("DISP:WIND:TRAC1:FEED 'Trc1'")
            self.vna.write('CALC1:FORM REAL')
            # time domain
            self.vna.write('CALC1:TRAN:TIME:STAT ON')
            self.vna.write('CALC1:TRAN:TIME LPAS; TIME:STIM STEP')
            time.sleep(1)
            self.vna.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')
            time.sleep(1)

        # -----------------------------------------------------------

        # Receive formatted measure
        self.vna.write("CALC1:PAR:SEL 'Trc1'")
        self.vna.write('CALC1:DATA? FDAT')
        yData = self.vna.read()
        #print(yData)

        # Receive S-parameters measure
        self.vna.write("CALC1:PAR:SEL 'Trc1'")
        self.vna.write('CALC1:DATA? SDAT')
        sData = self.vna.read()
        #print(sData)
        sDataArray = sData.split(",")
        #print(sDataArray)
        sDataArray = list(np.float_(sDataArray))
        #print(sDataArray)
        self.s_parameters = sDataArray
        #print(Sp)

        # Receive the number of point measured
        self.vna.write('CALC1:DATA:STIM?')
        xData = self.vna.read()
        #print(xData)

        yDataArray = yData.split(",")
        xDataArray = xData.split(",")

        yDataArray = list(np.float_(yDataArray))
        xDataArray = list(np.float_(xDataArray))

        return xDataArray, yDataArray


#==============================================================================#
    #for pick-up tests
    def pick_up(self, index):
        #self.vna.write('*RST') # Reset the instrument
        #self.vna.write('*CLS') # Clear the Error queue

        # Display update ON - switch OFF after debugging
        self.vna.write('SYST:DISP:UPD ON')

        if index == 0:
            # Receive measure
            self.vna.write("CALC1:PAR:SEL 'Trc1'")
            self.vna.write('CALC1:DATA? FDAT')
            yData = self.vna.read()
            #print(yData)

            # Receive the number of point measured
            self.vna.write('CALC1:DATA:STIM?')
            xData = self.vna.read()
            #print(xData)

            """
            # Receive S-parameters measure
            self.vna.write("CALC1:PAR:SEL 'Trc1'")
            self.vna.write('CALC1:DATA? SDAT')
            Sp = self.vna.read()
            self.s_parameters.append(Sp)
            #print(Sp)
            """

        elif index == 1:
            # Receive measure
            self.vna.write("CALC1:PAR:SEL 'Trc2'")
            self.vna.write('CALC1:DATA? FDAT')
            yData = self.vna.read()
            #print(yData)

            # Receive the number of point measured
            self.vna.write('CALC1:DATA:STIM?')
            xData = self.vna.read()
            #print(xData)

            # Receive S-parameters measure
            self.vna.write("CALC1:PAR:SEL 'Trc2'")
            self.vna.write('CALC1:DATA? SDAT')
            sData = self.vna.read()
            #print(sData)
            sDataArray = sData.split(",")
            #print(sDataArray)
            sDataArray = list(np.float_(sDataArray))
            #print(sDataArray)
            self.s_parameters = sDataArray
            #print(Sp)

        yDataArray = yData.split(",")
        xDataArray = xData.split(",")
        yDataArray = list(np.float_(yDataArray))
        xDataArray = list(np.float_(xDataArray))

        return xDataArray, yDataArray


#==============================================================================#
# if is used like a main
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    address = "TCPIP::CFO-MD-BQPVNA1::INSTR" #"TEST"
    test = Vna_measure(address, 1, 2) #test_type, chart_number

    while test.data_ready == False:
        print('wait')
        time.sleep(0.5)

    for i in range(len(test.measures)):
        x, y = test.measures[i]

        plt.title ("test")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.plot(x, y)
        plt.show()
