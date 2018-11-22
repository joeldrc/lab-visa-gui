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

    """
    # Sweep channel 1 only
    scope.write('INIT:SCOP SING')

    # Set START & STOP frequency
    scope.write('SENS1:FREQ:STAR ' + str(startFreq) + 'Ghz')
    scope.write('SENS1:FREQ:STOP ' + str(stopFreq) + 'Ghz')

    scope.write('SENS1:SWE:TYPE LIN')
    scope.write('SENS1:SWE:POIN ' + str(numPoints))
    print(scope.query('SENS1:SWE:POIN?'))

    # Set 10 sweeps per "INIT",
    # Average all 10 sweeps
    scope.write('SENS1:SWE:COUNT 10')
    scope.write('SENS1:AVER:COUN 10')
    scope.write('SENS1:AVER ON')

    # Manual sweep mode
    scope.write('INIT1:CONT OFF')

    # Start sweep         
    scope.write('INIT1')

    # Wait for sweeps to finish
    # Note: Set appropriate VISA timeout      
    opc_result = scope.query('*OPC?')
    print(opc_result)
    """

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

