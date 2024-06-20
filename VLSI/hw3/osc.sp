* Ring Oscillator using 15 Inverters
*----------------------------------------------------------------------
* Parameters and models
*----------------------------------------------------------------------
.param SUPPLY=1.8
.lib 'rf018.l' TT
.temp 70

*----------------------------------------------------------------------
* Simulation netlist
*----------------------------------------------------------------------
Vdd vdd gnd 'SUPPLY'
Vin in 0 0.817V

* Inverter chain
M1 out1 in gnd gnd nch W=500n L=200n
M2 out1 in vdd vdd pch W=1000n L=200n

M3 out2 out1 gnd gnd nch W=500n L=200n
M4 out2 out1 vdd vdd pch W=1000n L=200n

M5 out3 out2 gnd gnd nch W=500n L=200n
M6 out3 out2 vdd vdd pch W=1000n L=200n



* Initial condition to start oscillation
* .ic V(in)=0.01V

*simulation commands
.op
* .dc Vin 0 1.8V 0.01

*interactive interpretor command

* plot in vs out1
.MEASURE DC result FIND v(out3)

.end
