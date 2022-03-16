#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from time import gmtime, strftime
import pyvisa as visa
from PyQt5.QtCore import QRunnable, Qt, QThreadPool
import numpy as np


class VISA_Instrument(QRunnable):
    def __init__(self):
        super().__init__()
        self.address = ''
        self.calibration_name = ''
        self.test_name = ''
        self.file_name = ''
        self.directory_name = '' 
        self.data_ready = None
        self.info = 'NOT CONNECTED'
        self.type = ''
        self.measures = []
        self.png_file = []
        self.csv_file = []
        self.snp_file = []
        
    def run(self):                     
        print("VISA start")
        self.measures.clear()

        if (self.type == 'Demo'):
            self.info = self.type         
            x = np.linspace(0, 10, 101)
            y = np.sin(x + time.time())
            self.measures.append((x, y))

        elif (self.address == '_' or self.type == 'Demo'):
            self.info = 'TEST MODE'
            x = np.linspace(1, 301)
            y = np.sin(x) + np.random.normal(scale=0.1, size = len(x))
            self.measures.append((x, y))
      
        else:
            try:
                rm = visa.ResourceManager()
                print(rm.list_resources())

                self.vna = rm.open_resource(self.address)
                # Some instruments require that at the end of each command.
                self.vna.write_termination = '\n'
                #self.vna.read_termination = "\r"
                self.vna.timeout = 4000
                
                #read instrument info
                self.info = self.vna.query('*IDN?')  #Query the Identification string
                self.info = self.clean_string(self.info, clean_txt = True)
                print(self.info)
                #self.default_mode()
            except Exception as e:
                print(e)

        self.data_ready = True
        print('End run')

        

    def default_mode(self):
        if (self.test_name != '' and self.directory_name != ''):
            # Read default directory
            self.vna.write(':MMEMory:CDIRectory DEFault') # set to default
            default_dir = self.vna.query(':MMEMory:CDIRectory?') # read dir
            default_dir = self.clean_string(default_dir, clean_txt = True)
            pathname = default_dir + '\\' + self.directory_name + '\\'
            print(pathname)

            try:
                global calibration
                global device_address
                if (self.test_name != ''):
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
                    self.export_data(pathname + self.test_name, self.file_name + '_' + str(channel_number[i]), channel_number[i], self.port_number)
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
    def export_data(self, pathname, fileName, channel, port_number):
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
            val = '' # ",1,2"
            for i in range(port_number):
                val += ',' + str(i+1)

            self.vna.write(":MMEM:STOR:TRAC:PORT {}, '{}\\{}.s{}p', COMPlex{}".format(channel, pathname, fileName, port_number, val))
            print('sp saved')
            self.wait()
            # read S-parameters from VNA (.sp file)
            s_parameters = self.vna.query_binary_values(":MMEM:DATA? '{}\\{}.s{}p'".format(pathname, fileName, port_number), datatype='B', is_big_endian=False, container=bytearray)
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
