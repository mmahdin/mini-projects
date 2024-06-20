* Ring Oscillator using 15 Inverters
*----------------------------------------------------------------------
* Parameters and models
*----------------------------------------------------------------------
.param SUPPLY=1.8
.option scale=90n
.lib 'rf018.l' TT
.temp 70

*----------------------------------------------------------------------
* Simulation netlist
*----------------------------------------------------------------------
Vdd vdd gnd 'SUPPLY'

* Inverter chain
M1 out1 in gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M2 out1 in vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M3 out2 out1 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M4 out2 out1 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M5 out3 out2 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M6 out3 out2 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M7 out4 out3 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M8 out4 out3 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M9 out5 out4 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M10 out5 out4 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M11 out6 out5 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M12 out6 out5 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M13 out7 out6 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M14 out7 out6 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M15 out8 out7 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M16 out8 out7 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M17 out9 out8 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M18 out9 out8 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M19 out10 out9 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M20 out10 out9 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M21 out11 out10 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M22 out11 out10 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M23 out12 out11 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M24 out12 out11 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M25 out13 out12 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M26 out13 out12 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M27 out14 out13 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M28 out14 out13 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

M29 in out14 gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M30 in out14 vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

* Initial condition to start oscillation
.ic V(in)=0.01V

*----------------------------------------------------------------------
* Stimulus
*----------------------------------------------------------------------
.tran 0.1ps 10ns

*----------------------------------------------------------------------
* Measurement
*----------------------------------------------------------------------
.measure tplh * rising prop delay 
+ TRIG v(out1) VAL='SUPPLY/2' FALL=1 
+ TARG v(out2) VAL='SUPPLY/2' RISE=1
.measure tphl * falling prop delay 
+ TRIG v(out1) VAL='SUPPLY/2' RISE=1 
+ TARG v(out2) VAL='SUPPLY/2' FALL=1

.measure tran Ptotal integ par('i(Vdd)*v(Vdd)/10n') from 0 to 10ns

*----------------------------------------------------------------------
* End of File
*----------------------------------------------------------------------
.end
