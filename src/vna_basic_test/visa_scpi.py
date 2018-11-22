import time
import visa
import numpy as np
import matplotlib.pyplot as plt


vna_address = 'TCPIP::128.141.154.7::INSTR'


rm = visa.ResourceManager()
vna = rm.open_resource(vna_address)
vna.write_termination = '\n'  # Some instruments require LF at the end of each command. In that case, use:


"""
class Vna_measure():
    def __init__(self):
        rm = visa.ResourceManager()
        self.vna = rm.open_resource(vna_address)
        self.vna.write_termination = '\n'  # Some instruments require LF at the end of each command. In that case, use:
"""


def instrumentName():
    name = vna.query('*IDN?')   # Query the Identification string
    print(name)     
    return name


def vna_measure(index):
    #vna.write('*RST;*CLS')        # Reset the instrument, clear the Error queue
    vna.write('SYST:DISP:UPD ON') # Display update ON - switch OFF after debugging

    # -----------------------------------------------------------
    if index == 0:
        vna.write("CALC1:PAR:DEF 'Trc1', S21")
        vna.write('DISP:WIND:STAT ON')
        vna.write("DISP:WIND:TRAC1:FEED 'Trc1'")

        # marker
        vna.write('CALC1:MARK ON')
        vna.write('CALCulate1:MARKer1:X 2Ghz')
        
        vna.write('CALC1:FORM GDELay')
       
        time.sleep(1)
        vna.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')    
        time.sleep(1)

    # -----------------------------------------------------------
    elif index == 1:
        vna.write("CALC1:PAR:DEF 'Trc1', S21")
        vna.write('DISP:WIND:STAT ON')
        vna.write("DISP:WIND:TRAC1:FEED 'Trc1'")

        # marker
        vna.write('CALC1:MARK ON')
        vna.write('CALCulate1:MARKer1:X 2Ghz')
        
        vna.write('CALC1:FORM MLOG')
      
        time.sleep(1)
        vna.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')    
        time.sleep(1)

    # -----------------------------------------------------------
    elif index == 2:
        vna.write("CALC1:PAR:DEF 'Trc1', S11")
        vna.write('DISP:WIND:STAT ON')
        vna.write("DISP:WIND:TRAC1:FEED 'Trc1'")

        # marker
        vna.write('CALC1:MARK ON')
        vna.write('CALCulate1:MARKer1:X 2Ghz')

        vna.write('CALC1:FORM SWR')
          
        time.sleep(1)
        vna.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')    
        time.sleep(1)

    # -----------------------------------------------------------
    elif index == 3:
        vna.write("CALC1:PAR:DEF 'Trc1', S22")
        vna.write('DISP:WIND:STAT ON')
        vna.write("DISP:WIND:TRAC1:FEED 'Trc1'")

        # marker
        vna.write('CALC1:MARK ON')
        vna.write('CALCulate1:MARKer1:X 2Ghz')

        vna.write('CALC1:FORM SWR')
          
        time.sleep(1)
        vna.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')    
        time.sleep(1)

    # -----------------------------------------------------------
    elif index == 4:
        vna.write("CALC1:PAR:DEF 'Trc1', S11")
        vna.write('DISP:WIND:STAT ON')
        vna.write("DISP:WIND:TRAC1:FEED 'Trc1'")

        vna.write('CALC1:FORM REAL')

        # time domain
        vna.write('CALC1:TRAN:TIME:STAT ON')   
        vna.write('CALC1:TRAN:TIME LPAS; TIME:STIM STEP')
        
        time.sleep(1)    
        vna.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')    
        time.sleep(1)

    # -----------------------------------------------------------

    # measure
    vna.write("CALC1:PAR:SEL 'Trc1'")
    vna.write('CALC1:DATA? FDAT')
    yData = vna.read()
    #print(yData)

    # point of measure
    vna.write('CALC1:DATA:STIM?')
    xData = vna.read()
    #print(xData)
    
    yDataArray = yData.split(",")
    xDataArray = xData.split(",")

    yDataArray = list(np.float_(yDataArray))
    xDataArray = list(np.float_(xDataArray))

    """ 
    plt.title ("Trace Data via Python - PyVisa - SCPI")
    plt.xlabel("Frequency")
    plt.ylabel("Amplitude (dBm)")
    plt.plot(xDataArray, yDataArray)
    plt.show()
    """
    
    return(xDataArray, yDataArray)


"""
# Enable to test
instrumentName()    
for i in range(0, 5, 1):
    print(vna_measure(i))   
"""
  
