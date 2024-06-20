* inv.sp
*----------------------------------------------------------------------
* Parameters and models
*----------------------------------------------------------------------
.param SUPPLY=1.8
.option scale=90n
.lib 'rf018.l'  TT  
.temp 70

*----------------------------------------------------------------------
* Simulation netlist
*----------------------------------------------------------------------
Vdd vdd gnd 'SUPPLY'
Vin in gnd PULSE 0 'SUPPLY' 10ps 10ps 10ps 2ns 4ns

M1 out1 in gnd gnd nch W=3 L=2
+ AS=20 PS=18 AD=20 PD=18
M2 out1 in vdd vdd pch W=6 L=2
+ AS=40 PS=26 AD=40 PD=26

M3 out1 vdd out1 gnd nch W=6 L=2

M4 out2 out1 gnd gnd nch W=3 L=2
+ AS=20 PS=18 AD=20 PD=18
M5 out2 out1 vdd vdd pch W=6 L=2
+ AS=40 PS=26 AD=40 PD=26

M6 out2 vdd out2 gnd nch W=6 L=2

*----------------------------------------------------------------------
* Stimulus
*----------------------------------------------------------------------
.tran 0.1ps 4ns
.measure tplh * rising prop delay
+ TRIG v(in) VAL='SUPPLY/2' FALL=1
+ TARG v(out2) VAL='SUPPLY/2' RISE=1
.measure tphl * falling prop delay
+ TRIG v(in) VAL='SUPPLY/2' RISE=1
+ TARG v(out2) VAL='SUPPLY/2' FALL=1
.measure tp param='(tphl+tplh)/2' * average prop delay
.measure trise * rise time
+ TRIG v(out2) VAL='0.1*SUPPLY' RISE=1
+ TARG v(out2) VAL='0.9*SUPPLY' RISE=1
.measure tfall * fall time
+ TRIG v(out2) VAL='0.9*SUPPLY' FALL=1
+ TARG v(out2) VAL='0.1*SUPPLY' FALL=1
.end