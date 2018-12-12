import time
import visa
import numpy as np


class Vna_measure():
    
    def __init__(self, address):
        self.instrument_address = address
        rm = visa.ResourceManager()
        self.vna = rm.open_resource(self.instrument_address)
        self.vna.write_termination = '\n'  # Some instruments require that at the end of each command.


    def instrument_info(self):
        name = self.vna.query('*IDN?')  # Query the Identification string
        time.sleep(1)      
        print(name)     
        return (name, self.instrument_address)


    def read_measure(self, index):
        #self.vna.write('*RST') # Reset the instrument
        #self.vna.write('*CLS') # Clear the Error queue      
        self.vna.write('SYST:DISP:UPD ON') # Display update ON - switch OFF after debugging

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
       
        return(xDataArray, yDataArray)


"""
import matplotlib.pyplot as plt

# Enable to test
address = "TCPIP::CFO-MD-BQPVNA1::INSTR"
test = Vna_measure(address)
print(test.instrument_info())
for i in range(0, 5, 1):
    print(test.read_measure(i))

x, y = test.read_measure(0)

plt.title ("Trace Data via Python - PyVisa - SCPI")
plt.xlabel("Frequency")
plt.ylabel("Amplitude (dBm)")
plt.plot(x, y)
plt.show()
"""
