#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import visa
import threading
import numpy as np


class Vna_measure(threading.Thread):
    def __init__(self, address, test_type = 0):
        threading.Thread.__init__(self)

        self.instrument_address = address
        self.test_type = test_type

        self.instrument_info = ''
        self.data_ready = False
        self.measures = []
        self.s_parameters = []

        #start thread
        print("Init. visa setup")
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

        #start measures
        if self.test_mode == True:
            x = np.linspace(1, 301)
            y = np.sin(x) + np.random.normal(scale=0.1, size = len(x))
            self.measures.append((x, y))

        elif self.test_type == 1:
            #self.flanges()
            self.load_instrument_state('Automatic_tests\Feedthrought_test')
            self.read_data()

        elif self.test_type == 2:
            #self.pick_up()
            self.load_instrument_state('Automatic_tests\pick_up_test')
            self.read_data()

        else:
            print("exception")

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
    """
    # for flange tests
    def flanges(self):
        #self.vna.write('*RST') # Reset the instrument
        #self.vna.write('*CLS') # Clear the Error queue

        # Display update ON - switch OFF after debugging
        self.vna.write('SYST:DISP:UPD ON')

        # -----------------------------------------------------------
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

        # Receive the number of point measured
        self.vna.write('CALC1:DATA:STIM?')
        xData = self.vna.read()
        #print(xData)

        return format_values(xData, yData)
        """


#==============================================================================#
    def load_instrument_state(self, pathname):
        self.vna.write('*RST') # Reset the instrument
        self.vna.write('*CLS') # Clear the Error queue

        # Display update ON - switch OFF after debugging
        self.vna.write('SYST:DISP:UPD ON')

        #self.vna.write('MMEM:CDIR "C:\Program Files\Automatic_tests" ')
        print(self.vna.query('MMEMory:CDIRectory?'))

        #self.vna.write('MMEMory:STORe:STATe 1,"Automatic_tests\Feedthrought_test" ')
        #time.sleep(20)
        self.vna.write('MMEMory:LOAD:STATe 1,"%s" ' % (pathname))
        time.sleep(20)


#==============================================================================#
    def read_data(self):
        # read trace and measure type (Trc1, S21)
        trace_number = self.vna.query(':CALCULATE1:PARAMETER:CATALOG?')
        trace_number = trace_number.split(",")
        #print(len(trace_number))
        trace_number = trace_number[0::2]
        #print(trace_number)
        print(len(trace_number))

        for i in range(len(trace_number)):
            #select channel
            self.vna.write("CALC1:PAR:SEL 'Trc%d'" % (i + 1))

            # Receive measure
            self.vna.write('CALC1:DATA? FDAT')
            yData = self.vna.read()
            print(yData)

            # Receive the number of point measured
            self.vna.write('CALC1:DATA:STIM?')
            xData = self.vna.read()
            print(xData)

            yDataArray = yData.split(",")
            xDataArray = xData.split(",")
            yDataArray = list(np.float_(yDataArray))
            xDataArray = list(np.float_(xDataArray))

            self.measures.append((xDataArray, yDataArray))

        # read S-parameters from VNA
        self.s_parameters = self.vna.query("MMEM:DATA? 'Automatic_tests\Test_01.s2p' ")

        # remove new row
        self.s_parameters = self.s_parameters.replace("\r", "")
        print(self.s_parameters)


#==============================================================================#
# if is used like a main
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    address = "TCPIP::CFO-MD-BQPVNA1::INSTR" #"TEST"
    test = Vna_measure(address, 1) #test_type

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
