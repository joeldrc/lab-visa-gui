import visa
import numpy as npStimulusArray
import matplotlib.pyplot as plt


ip_address = '128.141.154.167'

numPoints = 201
startFreq = 0.3
stopFreq = 3


rm = visa.ResourceManager()
scope = rm.open_resource('TCPIP::' + ip_address + '::INSTR')

scope.write_termination = '\n'  # Some instruments require LF at the end of each command. In that case, use:

print(scope.query('*IDN?'))     # Query the Identification string
scope.write('*RST;*CLS')        # Reset the instrument, clear the Error queue
scope.write('SYST:DISP:UPD ON') # Display update ON - switch OFF after debugging


# -----------------------------------------------------------
# Basic Settings:
# -----------------------------------------------------------


# Sweep channel 1 only
scope.write('INIT:SCOP SING')

# Set START & STOP frequency
scope.write('SENS1:FREQ:STAR ' + str(startFreq) + 'Ghz')
scope.write('SENS1:FREQ:STOP ' + str(stopFreq) + 'Ghz')

scope.write('SENS1:SWE:TYPE LIN')
scope.write('SENS1:SWE:POIN ' + str(numPoints))
print(scope.query('SENS1:SWE:POIN?'))

"""
# Set 10 sweeps per "INIT",
# Average all 10 sweeps
scope.write('SENS1:SWE:COUNT 10')
scope.write('SENS1:AVER:COUN 10')
scope.write('SENS1:AVER ON')
"""

# Manual sweep mode
scope.write('INIT1:CONT OFF')

# Start sweep         
scope.write('INIT1')

# Wait for sweeps to finish
# Note: Set appropriate VISA timeout      
opc_result = scope.query('*OPC?')
print(opc_result)

# Query averaged, complex,
# unformatted Trc1 data
#scope.write("CALC2:PAR:SDEF 'Trc2', 'S11'")
scope.write("CALC1:PAR:SEL 'Trc1'")
scope.write('CALC1:DATA? FDAT')
traceData = scope.read()
print(traceData)

# point of measure
scope.write('CALC1:DATA:STIM?')
print(scope.read())


traceDataArray = traceData.split(",")
print(len(traceDataArray))

# Now plot the x - y data
maxResponseVal= max(traceDataArray)
minResponseVal = min(traceDataArray)

traceDataArray = list(npStimulusArray.float_(traceDataArray))
print(traceDataArray)

print ("Max value = " + maxResponseVal + " Min Value = " + minResponseVal)

xValuesArray = npStimulusArray.linspace(float(startFreq),float(stopFreq),int(numPoints))
print(xValuesArray)

#x = npStimulusArray.arange(len(traceDataArray))

plt.title ("Trace Data via Python - PyVisa - SCPI")
plt.xlabel("Frequency")
plt.ylabel("Amplitude (dBm)")
plt.plot(xValuesArray, traceDataArray)
plt.show()

