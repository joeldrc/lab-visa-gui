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

        self.start()    #start thread

    def run(self):
        print("Init. visa setup")

        if self.instrument_address == "TEST":   # TEST is used for debug
            self.instrument_info = 'TEST MODE ON'

            x = np.linspace(1, 301)
            y = np.sin(x) + np.random.normal(scale=0.1, size = len(x))
            self.measures.append((x, y))

        else:
            try:
                rm = visa.ResourceManager()
                self.vna = rm.open_resource(self.instrument_address)
                self.vna.write_termination = '\n'   # Some instruments require that at the end of each command.

                #read instrument info
                self.instrument_info = self.vna.query('*IDN?')                  #Query the Identification string
                self.instrument_info = self.instrument_info.replace("\r", "")   #remove new row
                print(self.instrument_info)

                #start measures
                if self.test_type == 1:
                    self.load_instrument_state('C:\Rohde&schwarz\\Nwa\Automatic_tests\\Feedthrought_test')

                elif self.test_type == 2:
                    self.load_instrument_state('C:\Rohde&schwarz\\Nwa\Automatic_tests\\pick_up_test')

                self.read_data()
                self.export_data('C:\Rohde&schwarz\\Nwa\Automatic_tests\\', 'Test_001')

                self.data_ready = True
                print('end measures')

            except Exception as e:
                print(e)
                self.instrument_info = 'NO CONNECTION'
                print(self.instrument_info)


#==============================================================================#
    def load_instrument_state(self, pathname):
        self.vna.write('*RST')  # Reset the instrument
        self.vna.write('*CLS')  # Clear the Error queue

        # Display update ON - switch OFF after debugging
        self.vna.write('SYST:DISP:UPD ON')

        # Read default directory
        print(self.vna.query('MMEMory:CDIRectory?'))

        #self.vna.write('MMEMory:STORe:STATe 1,"%s" ' % (pathname))
        #time.sleep(20)
        self.vna.write('MMEMory:LOAD:STATe 1,"%s" ' % (pathname))
        time.sleep(20)


#==============================================================================#
    def read_data(self):
        # read trace and measure type (Trc1, S21, ...)
        trace_number = self.vna.query(':CALCULATE1:PARAMETER:CATALOG?')
        trace_number = trace_number.split(",")
        trace_number = trace_number[0::2]
        print(trace_number)
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


#==============================================================================#
    def export_data(self, pathname, fileName):
        # create a new dir
        pathname = pathname + '\%s' % (fileName)
        print(pathname)

        self.vna.write("MMEM:MDIR '%s' " % (pathname))

        #file to save all traces
        self.vna.write("MMEM:STOR:TRAC:CHAN 1, '%s\%s.csv', FORMatted" % (pathname, fileName))

        #file to save S-Param
        self.vna.write("MMEM:STOR:TRAC:PORT  1, '%s\%s.s2p', COMPlex, 1,2" % (pathname, fileName))

        #file to save png
        self.vna.write("HCOP:DEV:LANG PNG")
        self.vna.write("MMEM:NAME '%s\%s.png' " % (pathname, fileName))
        self.vna.write("HCOP:MPAG:WIND ALL")
        self.vna.write("HCOP:DEST 'MMEM'; :HCOP")

        # read all traces from VNA (.csv file)
        self.all_traces = self.vna.query("MMEM:DATA? '%s\%s.csv' " % (pathname, fileName))
        self.all_traces = self.all_traces.replace("\r", "") #remove new row
        print(self.all_traces)

        # read S-parameters from VNA (.sp file)
        self.s_parameters = self.vna.query("MMEM:DATA? '%s\%s.s2p' " % (pathname, fileName))
        self.s_parameters = self.s_parameters.replace("\r", "") #remove new row
        print(self.s_parameters)

        # read pictures from VNA (.png file)
        self.vna.write("MMEM:DATA? '%s\%s.png' " % (pathname, fileName))
        self.picture = self.vna.read_raw()
        cutting_character = self.picture.find(b'\x89')
        self.picture = self.picture[cutting_character:] #remove characters up to \x89
        print(self.picture)


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


"""
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
"""
