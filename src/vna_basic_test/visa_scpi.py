import time
import visa
import numpy as np
import matplotlib.pyplot as plt

ip_address = '128.141.154.7'

def vna_measure():   
    rm = visa.ResourceManager()
    scope = rm.open_resource('TCPIP::' + ip_address + '::INSTR')
    scope.write_termination = '\n'  # Some instruments require LF at the end of each command. In that case, use:

    print(scope.query('*IDN?'))     # Query the Identification string
    #scope.write('*RST;*CLS')        # Reset the instrument, clear the Error queue
    scope.write('SYST:DISP:UPD ON') # Display update ON - switch OFF after debugging

    # -----------------------------------------------------------
    # Basic Settings:
    # -----------------------------------------------------------

    scope.write("CALC1:PAR:DEF 'Trc1', S21")
    scope.write('DISP:WIND:STAT ON')
    scope.write("DISP:WIND:TRAC1:FEED 'Trc1'")
    
    scope.write('CALC1:FORM GDELay')

    scope.query('*OPC?')
   
    time.sleep(1)
    scope.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')    
    time.sleep(1)

    # -----------------------------------------------------------
    
    scope.write("CALC1:PAR:DEF 'Trc1', S21")
    scope.write('DISP:WIND:STAT ON')
    scope.write("DISP:WIND:TRAC1:FEED 'Trc1'")
    
    scope.write('CALC1:FORM MLOG')

    scope.query('*OPC?')
   
    time.sleep(1)
    scope.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')    
    time.sleep(1)

    # -----------------------------------------------------------

    scope.write("CALC1:PAR:DEF 'Trc1', S11")
    scope.write('DISP:WIND:STAT ON')
    scope.write("DISP:WIND:TRAC1:FEED 'Trc1'")

    scope.write('CALC1:FORM SWR')
    
    scope.query('*OPC?')
   
    time.sleep(1)
    scope.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')    
    time.sleep(1)

    # -----------------------------------------------------------

    scope.write("CALC1:PAR:DEF 'Trc1', S22")
    scope.write('DISP:WIND:STAT ON')
    scope.write("DISP:WIND:TRAC1:FEED 'Trc1'")

    scope.write('CALC1:FORM SWR')
    
    scope.query('*OPC?')
   
    time.sleep(1)
    scope.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')    
    time.sleep(1)

    # -----------------------------------------------------------

    scope.write("CALC1:PAR:DEF 'Trc1', S11")
    scope.write('DISP:WIND:STAT ON')
    scope.write("DISP:WIND:TRAC1:FEED 'Trc1'")

    scope.write('CALC1:FORM REAL')

    # time domain
    scope.write('CALC1:TRAN:TIME:STAT ON')   
    scope.write('CALC1:TRAN:TIME LPAS; TIME:STIM STEP')
    
    time.sleep(1)    
    scope.write('DISP:WIND:TRAC1:Y:SCAL:AUTO ONCE')    
    time.sleep(1)
    
    # measure
    scope.write("CALC1:PAR:SEL 'Trc1'")
    scope.write('CALC1:DATA? FDAT')
    yData = scope.read()
    print(yData)

    # point of measure
    scope.write('CALC1:DATA:STIM?')
    xData = scope.read()
    print(xData)
    
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

# Enable to test
#vna_measure()

