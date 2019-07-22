#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from time import gmtime, strftime
import visa
import pyvisa as visa
import threading
import numpy as np


# Global variables
calibration = ''
loading_time = 20 #seconds


class Vna_measure(threading.Thread):
    def __init__(self, address, test_type = '', folder_name = 'data', test_name = 'test'):
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
        print("\nInit. visa setup\n")

        try:
            if self.instrument_address == "TEST":   # TEST is used for debug
                self.instrument_info = 'TEST MODE ON'
                x = np.linspace(1, 301)
                y = np.sin(x) + np.random.normal(scale=0.1, size = len(x))
                self.measures.append((x, y))

            else:
                rm = visa.ResourceManager()
                self.vna = rm.open_resource(self.instrument_address)
                self.vna.write_termination = '\n'   # Some instruments require that at the end of each command.

                #read instrument info
                self.instrument_info = self.vna.query('*IDN?')  #Query the Identification string
                self.instrument_info = self.clean_string(self.instrument_info, clean_txt = True)
                print(self.instrument_info)

                # Read default directory
                default_dir = self.vna.query('MMEMory:CDIRectory?') # 'C:\Rohde&schwarz\\Nwa'
                default_dir = self.clean_string(default_dir, clean_txt = True)
                print(default_dir)

                try:
                    pathname = default_dir + '\\Automatic_tests\\'
                    print(pathname)
                    typeName = '%s_test.zvx' % (self.test_type)

                    if self.test_type > '':
                        global calibration
                        if (calibration != self.test_type):
                            self.load_instrument_state(pathname + typeName)
                            calibration = self.test_type

                        self.auto_scale_screen()
                        self.read_data()
                        self.export_data(pathname + self.test_type + '_' + self.folder_name, self.test_name)
                        print('End measures')

                except Exception as e:
                    print(e)

            #self.data_ready = True

        except Exception as e:
            print(e)
            self.instrument_info = 'NO CONNECTION'
            print(self.instrument_info)

        self.data_ready = True


#==============================================================================#
    def clean_string(self, string, clean_txt = False):
        string = string.replace("'", "")
        string = string.replace("\r", "")
        string = string.replace("\n", "")

        if clean_txt == False:
            string = string.split(",")

        return string


#==============================================================================#
    def wait(self, seconds = 0):
        if (seconds > 0):
            time.sleep(seconds)

        # Wait until the command is executed
        msg = self.vna.query('*WAI; *OPC?')
        #print(msg)


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
    def auto_scale_screen(self):
        # read windows number (1, 1, ...)
        windows_number = self.vna.query("DISPlay:WINDow:CATalog? ")
        self.wait()

        windows_number = self.clean_string(windows_number)
        print(windows_number)
        windows_number = windows_number[0::2]
        print(windows_number)

        for i in range(len(windows_number)):
            # read trace in window (1,Trc1, ...)
            trace_number = self.vna.query("DISPlay:WINDow%d:TRACe:CATalog?" % (i + 1))
            self.wait()

            trace_number = self.clean_string(trace_number)
            print(trace_number)
            trace_number = trace_number[0::2]
            print(trace_number)

            for j in range(len(trace_number)):
                self.vna.write("DISPlay:WINDow%d:TRACe%d:Y:SCALe:AUTO ONCE" % (i + 1, int(trace_number[j])))
                self.wait()

                print('autoscale window %d and trace %d' % (i + 1, int(trace_number[j])))


#==============================================================================#
    def read_data(self):
        # read trace and measure type (Trc1, S21, ...)
        trace_number = self.vna.query(':CALCULATE1:PARAMETER:CATALOG?')
        self.wait()

        trace_number = self.clean_string(trace_number)
        print(trace_number)
        trace_number = trace_number[0::2]
        print(trace_number)

        for i in range(len(trace_number)):
            #select channel
            self.vna.write("CALC1:PAR:SEL 'Trc%d'" % (i + 1))
            self.wait()

            # Receive measure
            yData = self.vna.query('CALC1:DATA? FDAT')
            #print(yData)
            self.wait()

            # Receive the number of point measured
            xData = self.vna.query('CALC1:DATA:STIM?')
            #print(xData)
            self.wait()

            yDataArray = yData.split(",")
            xDataArray = xData.split(",")
            yDataArray = list(np.float_(yDataArray))
            xDataArray = list(np.float_(xDataArray))

            self.measures.append((xDataArray, yDataArray))


#==============================================================================#
    def export_data(self, pathname, fileName):
        # check if the current DIR already exist
        check_folder = self.vna.query("MMEM:CAT? '%s' " % (pathname))
        print(len(check_folder))
        self.wait()

        if (len(check_folder) <= 1):
            self.vna.write('*CLS')  # Clear the Error queue

            # create a new dir in the vna
            print("create a new DIR")
            self.vna.write("MMEM:MDIR '%s' " % (pathname))
            self.wait()

        # save all traces
        self.vna.write("MMEM:STOR:TRAC:CHAN 1, '%s\%s.csv', FORMatted" % (pathname, fileName)) #MMEM:STOR:TRAC:CHAN {}
        self.wait()
        # read all traces from VNA (.csv file)
        self.all_traces = self.vna.query_binary_values("MMEM:DATA? '%s\%s.csv' " % (pathname, fileName), datatype='B', is_big_endian=False, container=bytearray)
        #print(self.all_traces)
        self.wait()

        # save S-Param
        self.vna.write("MMEM:STOR:TRAC:PORT 1, '%s\%s.s2p', COMPlex, 1,2" % (pathname, fileName))
        self.wait()
        # read S-parameters from VNA (.sp file)
        self.s_parameters = self.vna.query_binary_values("MMEM:DATA? '%s\%s.s2p' " % (pathname, fileName), datatype='B', is_big_endian=False, container=bytearray)
        #print(self.s_parameters)
        self.wait()

        # save png file
        self.vna.write("HCOP:DEV:LANG PNG")
        self.vna.write("MMEM:NAME '%s\%s.png' " % (pathname, fileName))
        self.vna.write("HCOP:MPAG:WIND ALL")
        self.vna.write("HCOP:DEST 'MMEM'; :HCOP")
        self.wait()
        # read pictures from VNA (.png file)
        self.picture = self.vna.query_binary_values("MMEM:DATA? '%s\%s.png' " % (pathname, fileName), datatype='B', is_big_endian=False, container=bytearray)
        #print(self.picture)
        self.wait()


#==============================================================================#
# if is used like a main
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    print("Python test software 2019\n")

    while(1):
        run_script =  input('Continue [y/n](enter to default)?:')
        if run_script == '':
            run_script = 'y'   #default
        print('-> ', run_script)
        if run_script != 'y':
            break

        address = input('Enter address (enter to default):')
        if address == '':
            address = "TCPIP::CFO-MD-BQPVNA1::INSTR"    #default, you can also chose "TEST"
        print('-> ', address)

        test_name = input('Enter test name (enter to default):')
        if test_name == '':
            test_name = 'Feedthrough'   #default
        print('-> ', test_name)

        save_files = input('Save files [y/n](enter to default)?:')
        if save_files == '':
            save_files = 'n'   #default
        print('-> ', save_files)

        test = Vna_measure(address, test_name)

        i = 0
        while test.data_ready == False:
            s = str(i) + '%'    # string for output
            print('wait: ' + s, end='')    # just print and flush
            # back to the beginning of line
            print('\r', end='') # use '\r' to go back
            time.sleep(0.5)
            i += 1

        for i in range(len(test.measures)):
            x, y = test.measures[i]
            plt.title ("test")
            plt.xlabel("x")
            plt.ylabel("y")
            plt.plot(x, y)
            plt.show()

        if save_files == 'y':

            name = strftime("%d%m%Y_%H%M%S", gmtime())

            # Save all files received from vna
            print("Saving files")

            # export sp file
            file = open(name + '.s2p',"wb")
            file.write(test.s_parameters)
            file.close()
            print('File saved')

            # export csv file
            file = open(name + '.csv',"wb")
            file.write(test.all_traces)
            file.close()
            print('File saved')

            # export png files
            file = open(name + '.png',"wb")
            file.write(test.picture)
            file.close()
            print('File saved')
