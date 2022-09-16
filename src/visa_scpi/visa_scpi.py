# -*- coding: utf-8 -*-
# Joel Daricou 09/2022

from cgi import test
from pickletools import read_stringnl_noescape_pair
import time
from time import gmtime, strftime
import pyvisa as visa
import numpy as np

#global 
calibration =''
address = ''
                    
class Instrument_VISA():
    def __init__(self, address = '', setup = '', calib = False):
        super().__init__()
        self.device_address = address
        self.setup_name = setup
        self.force_calib = calib

        self.directory_path = 'C:\\Users\\Public\\Documents\\Network Analyzer\\automatic_tests'
        self.file_name = 'fileData'

        self.data_dict = {}
        self.data_dict['devices'] = None
        self.data_dict['instr_info'] = None
        self.data_dict['form_data'] = []
        self.data_dict['png_file'] = []
        self.data_dict['csv_file'] = []
        self.data_dict['snp_file'] = []

        self.scpi_cmd = {}

    def run(self):    
            print("VISA setup")
            try:
                rm = visa.ResourceManager()
                self.data_dict['devices'] = rm.list_resources()             
                print("Devices: ", self.data_dict['devices'])
                vna = rm.open_resource(self.device_address)

                # Some instruments require that at the end of each command.
                vna.write_termination = '\n' #"\r"
                vna.timeout = 10000
                
                # Read instrument info
                self.data_dict['instr_info'] = vna.query('*IDN?')  #Query the Identification string
                print(self.data_dict['instr_info'])

                # Detect instrument
                instr_name = self.data_dict['instr_info']    

                if instr_name.find("Rohde-Schwarz") != -1:
                    pass
                    
                elif instr_name.find("Keysight") != -1:    
                    self.scpi_cmd['list_files'] = 'MMEM:CAT?'
                    self.scpi_cmd['change_dir'] = 'MMEM:CDIR "{}"'.format(self.directory_path)
                    self.scpi_cmd['load_state'] = 'MMEM:LOAD "{}.csa"'.format(self.setup_name)
                    #self.scpi_cmd['read_data'] = 'CALC:DATA? FDAT'
                    self.scpi_cmd['save_snp'] = 'MMEM:STOR "{}.S4P"'.format(self.file_name)
                    self.scpi_cmd['save_png'] = 'MMEMory:STORe:SSCReen "{}.bmp"'.format(self.file_name)
                    self.scpi_cmd['save_csv'] = 'MMEMory:STORe:DATA "{}.csv","CSV Formatted Data","Displayed","Displayed", -1'.format(self.file_name)
                    self.scpi_cmd['read_csv'] = 'MMEMory:TRANsfer? "{}.csv"'.format(self.file_name)
                    self.scpi_cmd['read_snp'] = 'MMEMory:TRANsfer? "{}.s4p"'.format(self.file_name)
                    self.scpi_cmd['read_png']=  'MMEMory:TRANsfer? "{}.bmp"'.format(self.file_name)

                elif instr_name.find("Agilent") != -1:
                    pass

                else:
                    print("Unknown instrument")

                #start measure
                if (self.setup_name != '_'):
                    print('start measure: ', self.setup_name)
                    #Set default directory
                    vna.write(self.scpi_cmd['change_dir'])
                    vna.query(';*OPC?')

                    global calibration
                    global address
                    if ((calibration != self.setup_name) or (self.device_address != address) or (self.force_calib == True)):
                        #load calibration
                        print('load calibration')
                        calibration = self.setup_name
                        address = self.device_address                           
                        vna.write(self.scpi_cmd['load_state'])
                        time.sleep(20)
                        vna.query(';*OPC?')

                    print('save csv')
                    vna.write(self.scpi_cmd['save_csv'])
                    vna.query(';*OPC?')                  
                    print('save snp')
                    vna.write(self.scpi_cmd['save_snp'])
                    vna.query(';*OPC?')
                    print('save screenshot')
                    vna.write(self.scpi_cmd['save_png'])
                    vna.query(';*OPC?')

                    print('read csv')
                    self.data_dict['csv_file'] = vna.query(self.scpi_cmd['read_csv'])
                    vna.query(';*OPC?')       
                    print('read snp')
                    self.data_dict['snp_file'] = vna.query(self.scpi_cmd['read_snp'])
                    vna.query(';*OPC?')
                    print('read png')
                    self.data_dict['png_file'] = vna.query_binary_values(self.scpi_cmd['read_png'], datatype='B', is_big_endian=False, container=bytearray)
                    vna.query(';*OPC?')

                    print('extract form data')
                    self.data_dict['form_data'] = self.extract_csv(self.data_dict['csv_file'])

            except Exception as e:
                print(e, "Instrument not connected")

                # Demo and test plot
                if (self.device_address == 'Demo'):
                    self.data_dict['instr_info'] = self.device_address
                    x = np.linspace(0, 10, 101)
                    y = np.sin(x + time.time())
                    self.data_dict['form_data'].append([x, y])
                elif (self.device_address == 'Test'):
                    self.data_dict['instr_info'] = self.device_address
                    x = np.linspace(1, 301)
                    y = np.sin(x) + np.random.normal(scale=0.1, size = len(x))
                    self.data_dict['form_data'].append([x, y])
                else:
                    self.data_dict['instr_info'] = "Instrument not connected"
                    self.data_dict['form_data'] = ''
                    self.data_dict['png_file'] = ''
                    self.data_dict['csv_file'] = ''
                    self.data_dict['snp_file'] = ''

            print('End run')
            return self.data_dict

    def extract_csv(self, file):  
        #clean data
        file = file.replace("\r", '')
        values = file.split("\n")
        
        #extract data
        begin = []
        end = []
        for i in range(len(values)):
            if values[i].find('BEGIN') == 0:
                begin.append(i+2) #skip the first two rows
            elif values[i].find('END') == 0:
                end.append(i-1) #skip the first row

        data = []
        for b, e in zip(begin, end):
            val_x = []
            val_y = []
            for row in values[b:e]:                
                x, y = row.split(",")    
                val_x.append(np.float_(x))
                val_y.append(np.float_(y))
                
            data.append([val_x, val_y])
            
        return data
