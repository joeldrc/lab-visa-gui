#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import visa
import numpy as np


class Vna_measure():
    def __init__(self, address):
        print("Init. visa setup")
        self.instrument_address = address

        # TEST is used for debug
        if self.instrument_address == "TEST":
            self.test_mode = True
        else:
            self.test_mode = False

            rm = visa.ResourceManager()
            self.vna = rm.open_resource(self.instrument_address)
            # Some instruments require that at the end of each command.
            self.vna.write_termination = '\n'


    def instrument_info(self):
        if self.test_mode == True:
            name = 'TEST MODE ON \n'
        else:
            name = self.vna.query('*IDN?')  # Query the Identification string
        time.sleep(1)
        return name

    # return random numbers
    def read_measure(self, value, index):
        if self.test_mode == True:
            x = np.linspace(1, 301)
            y = np.sin(x) + np.random.normal(scale=0.1, size = len(x))
            return x, y

        elif value == 0:
            return self.flanges(index)

        elif value == 1:
            return self.pick_up(index)

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

        # Receive measure
        self.vna.write("CALC1:PAR:SEL 'Trc1'")
        self.vna.write('CALC1:DATA? FDAT')
        yData = self.vna.read()
        #print(yData)

        # Receive the number of point measured
        self.vna.write('CALC1:DATA:STIM?')
        xData = self.vna.read()
        #print(xData)

        yDataArray = yData.split(",")
        xDataArray = xData.split(",")

        yDataArray = list(np.float_(yDataArray))
        xDataArray = list(np.float_(xDataArray))

        return xDataArray, yDataArray

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

        elif index == 1:
            # Receive measure
            self.vna.write("CALC2:PAR:SEL 'Trc2'")
            self.vna.write('CALC2:DATA? FDAT')
            yData = self.vna.read()
            #print(yData)
            # Receive the number of point measured
            self.vna.write('CALC2:DATA:STIM?')
            xData = self.vna.read()
            #print(xData)

        yDataArray = yData.split(",")
        xDataArray = xData.split(",")
        yDataArray = list(np.float_(yDataArray))
        xDataArray = list(np.float_(xDataArray))

        return xDataArray, yDataArray


# if is used like a main
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    try:
        address = "TCPIP::CFO-MD-BQPVNA1::INSTR" #"TEST"
        test = Vna_measure(address)
        print(test.instrument_info())

        values = []
        for i in range(0, 5, 1):
            #x, y = test.read_measure_2(i)
            values.append(test.read_measure(0, i))
            x, y = values[i]
            print(x)
            print(y)

            plt.title ("Trace Data via Python - PyVisa - SCPI")
            plt.xlabel("Frequency")
            plt.ylabel("Amplitude (dBm)")
            plt.plot(x, y)
            plt.show()
    except Exception as e:
        print(e)
