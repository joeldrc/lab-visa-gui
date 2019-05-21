#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import visa
import threading
import numpy as np


# Global variables
calibration = 0
loading_time = 20 #seconds


class Vna_measure(threading.Thread):
    def __init__(self, address, test_type = 0, folder_name = 'none', test_name = 'none'):
        threading.Thread.__init__(self)

        self.instrument_address = address
        self.test_type = test_type
        self.folder_name = folder_name
        self.test_name = test_name
        self.measures = []
        self.instrument_info = ''
        self.data_ready = False

        self.start() # Start thread

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

                # Read default directory
                print(self.vna.query('MMEMory:CDIRectory?'))

                #start measures
                if self.test_type == 1:
                    pathname = 'C:\Rohde&schwarz\\Nwa\Automatic_tests\\Feedthrough\\'
                    typeName = 'Feedthrough_test.zvx'

                elif self.test_type == 2:
                    pathname = 'C:\Rohde&schwarz\\Nwa\Automatic_tests\\Pick_up\\'
                    typeName = 'Pick_up_test.zvx'

                if self.test_type > 0:
                    global calibration
                    if (calibration != self.test_type):
                        self.load_instrument_state(pathname + typeName)
                        calibration = self.test_type

                    self.read_data()
                    self.export_data(pathname + self.folder_name, self.test_name)
                    print('End measures')

                self.data_ready = True

            except Exception as e:
                print(e)
                self.instrument_info = 'NO CONNECTION'
                print(self.instrument_info)


#==============================================================================#
    def wait(self, seconds = 0):
        if (seconds > 0):
            time.sleep(seconds)

        # Wait until the command is executed
        print(self.vna.query('*WAI; *OPC?'))


#==============================================================================#
    def load_instrument_state(self, pathname):
        self.vna.write('*RST')  # Reset the instrument
        self.vna.write('*CLS')  # Clear the Error queue

        # Set display update ON
        self.vna.write('SYST:DISP:UPD ON')

        # load instrument state
        self.vna.write('MMEMory:LOAD:STATe 1,"%s" ' % (pathname)) # Use 'STORe' to save the setup
        global loading_time
        self.wait(loading_time)


#==============================================================================#
    def read_data(self):
        # read trace and measure type (Trc1, S21, ...)
        trace_number = self.vna.query(':CALCULATE1:PARAMETER:CATALOG?')
        self.wait()

        trace_number = trace_number.split(",")
        trace_number = trace_number[0::2]
        print(trace_number)

        for i in range(len(trace_number)):
            #select channel
            self.vna.write("CALC1:PAR:SEL 'Trc%d'" % (i + 1))
            self.wait()

            # Receive measure
            yData = self.vna.query('CALC1:DATA? FDAT')
            print(yData)
            self.wait()

            # Receive the number of point measured
            xData = self.vna.query('CALC1:DATA:STIM?')
            print(xData)
            self.wait()

            yDataArray = yData.split(",")
            xDataArray = xData.split(",")
            yDataArray = list(np.float_(yDataArray))
            xDataArray = list(np.float_(xDataArray))

            self.measures.append((xDataArray, yDataArray))


#==============================================================================#
    def export_data(self, pathname, fileName):
        # create a new dir in the vna
        self.vna.write("MMEM:MDIR '%s' " % (pathname))
        self.wait()

        #file to save all traces
        self.vna.write("MMEM:STOR:TRAC:CHAN 1, '%s\%s.csv', FORMatted" % (pathname, fileName)) #MMEM:STOR:TRAC:CHAN {}
        self.wait()

        #file to save S-Param
        self.vna.write("MMEM:STOR:TRAC:PORT 1, '%s\%s.s2p', COMPlex, 1,2" % (pathname, fileName))
        self.wait()

        # save png file
        self.vna.write("HCOP:DEV:LANG PNG")
        self.vna.write("MMEM:NAME '%s\%s.png' " % (pathname, fileName))
        self.vna.write("HCOP:MPAG:WIND ALL")
        self.vna.write("HCOP:DEST 'MMEM'; :HCOP")
        self.wait()

        # read all traces from VNA (.csv file)
        self.all_traces = self.vna.query_binary_values("MMEM:DATA? '%s\%s.csv' " % (pathname, fileName), datatype='B', is_big_endian=False, container=bytearray)
        print(self.all_traces)
        self.wait()

        # read S-parameters from VNA (.sp file)
        self.s_parameters = self.vna.query_binary_values("MMEM:DATA? '%s\%s.s2p' " % (pathname, fileName), datatype='B', is_big_endian=False, container=bytearray)
        print(self.s_parameters)
        self.wait()

        # read pictures from VNA (.png file)
        self.picture = self.vna.query_binary_values("MMEM:DATA? '%s\%s.png' " % (pathname, fileName), datatype='B', is_big_endian=False, container=bytearray)
        print(self.picture)
        self.wait()


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
# -----------------------------------------------------------
# read all traces from VNA (.csv file)
#self.all_traces = self.vna.query("MMEM:DATA? '%s\%s.csv' " % (pathname, fileName))
#self.all_traces = self.all_traces.replace("\r", "") #remove new row

# -----------------------------------------------------------
# read S-parameters from VNA (.sp file)
#self.s_parameters = self.vna.query("MMEM:DATA? '%s\%s.s2p' " % (pathname, fileName))
#self.s_parameters = self.s_parameters.replace("\r", "") #remove new row

# -----------------------------------------------------------
# read pictures from VNA (.png file)
#self.vna.write("MMEM:DATA? '%s\%s.png' " % (pathname, fileName))
#self.picture = self.vna.read_raw()
#cutting_character = self.picture.find(b'\x89')
#self.picture = self.picture[cutting_character:] #remove characters up to \x89

# -----------------------------------------------------------
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
