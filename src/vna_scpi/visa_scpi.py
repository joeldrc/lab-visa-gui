#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from time import gmtime, strftime
import visa
import pyvisa as visa
import threading
import numpy as np


# Global variables
calibration = 'none'
device_address = 'none'
loading_time = 20 #seconds


class Vna_measure(threading.Thread):
    def __init__(self, instrument_address = 'null', test_name = 'null', file_name = 'null', directory_name = 'null'):
        threading.Thread.__init__(self)

        self.instrument_address = instrument_address
        self.test_name = test_name
        self.file_name = file_name
        self.directory_name = directory_name

        self.measures = []
        self.picture = []
        self.all_traces = []
        self.s_parameters = []

        self.instrument_info = 'NOT CONNECTED'
        self.data_ready = False

        # Start thread
        self.start()

    def run(self):
        print("Init. visa setup")
        if (self.instrument_address == ''):
            self.instrument_info = 'TEST MODE'
            print(self.instrument_info)
            self.test_mode()
        else:
            try:
                rm = visa.ResourceManager()
                self.vna = rm.open_resource(self.instrument_address)
                self.vna.write_termination = '\n'   # Some instruments require that at the end of each command.
                #self.vna.read_termination = "\r"
                self.vna.timeout = 4000
                self.vna.write('*CLS')  # Clear the Error queue

                #read instrument info
                self.instrument_info = self.vna.query('*IDN?')  #Query the Identification string
                self.instrument_info = self.clean_string(self.instrument_info, clean_txt = True)
                print(self.instrument_info)
                self.default_mode()
            except Exception as e:
                print(e)

        self.data_ready = True


    def test_mode(self):
        # random measures
        x = np.linspace(1, 301)
        y = np.sin(x) + np.random.normal(scale=0.1, size = len(x))
        self.measures.append((x, y))


    def default_mode(self):
        if (self.test_name != 'null' and self.directory_name != 'null'):
            # Read default directory
            self.vna.write(':MMEMory:CDIRectory DEFault') # set to default
            default_dir = self.vna.query(':MMEMory:CDIRectory?') # read dir
            default_dir = self.clean_string(default_dir, clean_txt = True)
            pathname = default_dir + '\\' + self.directory_name + '\\'
            print(pathname)

            try:
                global calibration
                global device_address
                if ((calibration != self.test_name) or (device_address != self.instrument_address)):
                    self.load_instrument_state(pathname + self.test_name)
                    calibration = self.test_name
                    device_address = self.instrument_address

                self.auto_scale_screen()

                #detect number of channels
                print('number of channels')
                channel_number = self.vna.query(':CONFigure:CHANnel:CATalog?')
                channel_number = self.clean_string(channel_number)
                #print(channel_number)
                channel_number = channel_number[0::2]
                print(channel_number)

                for i in range(len(channel_number)):
                    self.read_data(channel_number[i])
                    self.export_data(pathname + self.test_name, self.file_name + '_' + str(channel_number[i]), channel_number[i])
                print('End measures')

            except Exception as e:
                print(e)


#==============================================================================#
    def clean_string(self, string, clean_txt = False):
        string = string.replace("'", "")
        string = string.replace("\r", "")
        string = string.replace("\n", "")

        if clean_txt == False:
            string = string.split(",")

        return string


#==============================================================================#
    def wait(self, seconds = 0.5):
        if (seconds > 0):
            time.sleep(seconds)
        # Wait until the command is executed
        #msg = self.vna.query('*WAI; *OPC?')
        #print(msg)


#==============================================================================#
    def load_instrument_state(self, pathname):
        self.vna.write('*RST')  # Reset the instrument
        # Set display update ON
        self.vna.write(':SYST:DISP:UPD ON')
        # load instrument state
        self.vna.write(':MMEMory:LOAD:STATe 1,"{}" '.format(pathname)) # Use 'STORe' to save the setup
        global loading_time
        self.wait(loading_time)


#==============================================================================#
    def auto_scale_screen(self):
        # read windows number (1, 1, ...)
        windows_number = self.vna.query(":DISPlay:WINDow:CATalog?")
        self.wait()

        windows_number = self.clean_string(windows_number)
        print(windows_number)
        windows_number = windows_number[0::2]
        print(windows_number)

        for i in range(len(windows_number)):
            # read trace in window (1,Trc1, ...)
            trace_number = self.vna.query(":DISPlay:WINDow{}:TRACe:CATalog?".format(i + 1))
            self.wait()

            trace_number = self.clean_string(trace_number)
            print(trace_number)
            trace_number = trace_number[0::2]
            print(trace_number)

            for j in range(len(trace_number)):
                self.vna.write(":DISPlay:WINDow{}:TRACe{}:Y:SCALe:AUTO ONCE".format(i + 1, int(trace_number[j])))
                self.wait()

                print('autoscale window {} and trace {}'.format(i + 1, int(trace_number[j])))


#==============================================================================#
    def read_data(self, channel = 1):
        # read trace and measure type (Trc1, S21, ...)
        trace_number = self.vna.query(':CALCULATE{}:PARAMETER:CATALOG?'.format(channel))
        self.wait()

        trace_number = self.clean_string(trace_number)
        print(trace_number)
        trace_number = trace_number[0::2]
        print(trace_number)

        for i in range(len(trace_number)):
            #select channel
            self.vna.write(":CALC{}:PAR:SEL '{}'".format(channel, trace_number[i])) # Trc{}
            self.wait()

            # Receive measure
            yData = self.vna.query(':CALC{}:DATA? FDAT'.format(channel))
            #print(yData)
            self.wait()

            # Receive the number of point measured
            xData = self.vna.query(':CALC{}:DATA:STIM?'.format(channel))
            #print(xData)
            self.wait()

            yDataArray = yData.split(",")
            xDataArray = xData.split(",")
            yDataArray = list(np.float_(yDataArray))
            xDataArray = list(np.float_(xDataArray))

            self.measures.append((xDataArray, yDataArray))


#==============================================================================#
    def export_data(self, pathname, fileName, channel = 1):
        # check if the current DIR already exist
        check_folder = self.vna.query(":MMEM:CAT? '{}'".format(pathname))
        print(len(check_folder))
        self.wait()

        if (len(check_folder) <= 1):
            self.vna.write('*CLS')  # Clear the Error queue
            # create a new dir in the vna
            print("create a new DIR")
            self.vna.write(":MMEM:MDIR '{}' ".format(pathname))
            self.wait()

        try:
            # save all traces
            self.vna.write(":MMEM:STOR:TRAC:CHAN {}, '{}\\{}.csv', FORMatted".format(channel, pathname, fileName)) #MMEM:STOR:TRAC:CHAN
            print('csv saved')
            self.wait()
            # read all traces from VNA (.csv file)
            all_traces = self.vna.query_binary_values(":MMEM:DATA? '{}\\{}.csv'".format(pathname, fileName), datatype='B', is_big_endian=False, container=bytearray)
            self.all_traces.append(all_traces)
            print('csv read')
            #print(self.all_traces)
            self.wait()
        except Exception as e:
            print(e)

        try:
            # save S-Param
            self.vna.write(":MMEM:STOR:TRAC:PORT {}, '{}\\{}.s2p', COMPlex, 1,2".format(channel, pathname, fileName))
            print('sp saved')
            self.wait()
            # read S-parameters from VNA (.sp file)
            s_parameters = self.vna.query_binary_values(":MMEM:DATA? '{}\\{}.s2p'".format(pathname, fileName), datatype='B', is_big_endian=False, container=bytearray)
            self.s_parameters.append(s_parameters)
            print('sp read')
            #print(self.s_parameters)
            self.wait()
        except Exception as e:
            print(e)

        try:
            # save png file
            self.vna.write("HCOP:DEV:LANG PNG")
            self.vna.write("MMEM:NAME '%s\\%s.png' " % (pathname, fileName))
            #self.vna.write("HCOP:MPAG:WIND ALL")
            self.vna.write("HCOP:DEST 'MMEM'; :HCOP")
            print('png saved')
            self.wait()
            # read pictures from VNA (.png file)
            self.picture = self.vna.query_binary_values("MMEM:DATA? '%s\\%s.png' " % (pathname, fileName), datatype='B', is_big_endian=False, container=bytearray)
            print('png read')
            #print(self.picture)
            self.wait()
        except Exception as e:
            print(e)


#==============================================================================#
# if is used like a main
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    print("Python test software 2019")

    while(1):
        run_script =  input('Press to enter to Continue: ')

        address = input('Enter address (enter to default): ')
        if address == '':
            print('-> TEST MODE ON')
        else:
            print('->', address)

        test_name = input('Enter test name (enter to default): ')
        if test_name == '':
            print('-> DEMO')
        else:
            print('->', test_name)

        save_files = input('Save files [y/n]: ')
        if save_files == '':
            save_files = 'n'   #default
        print('->', save_files)

        test = Vna_measure(instrument_address = address, test_name = test_name, file_name = 'null', directory_name = 'Automatic_tests')

        i = 0
        while (test.data_ready == False):
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

        if (save_files == 'y'):
            name = strftime("%d%m%Y_%H%M%S", gmtime())

            # Save all files received from vna
            print("Saving files")

            # export png files
            file = open(name + '.png',"wb")
            file.write(test.picture)
            file.close()
            print('File saved')

            for i in range(len(test.all_traces)):
                # export csv file
                file = open(name + str(i) + '.csv',"wb")
                file.write(test.all_traces[i])
                file.close()
                print('File saved' + str(i))

            for i in range(len(test.s_parameters)):
                # export sp file
                file = open(name + str(i) + '.s2p',"wb")
                file.write(test.s_parameters[i])
                file.close()
                print('File saved' + str(i))
