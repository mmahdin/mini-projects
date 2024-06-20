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
M1 out in gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M2 out in vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26
C1 out 0 20fF
*----------------------------------------------------------------------
* Stimulus
*----------------------------------------------------------------------
.tran 0.1ps 4ns
.measure tplh * rising prop delay
+ TRIG v(in) VAL='SUPPLY/2' FALL=1
+ TARG v(out) VAL='SUPPLY/2' RISE=1
.measure tphl * falling prop delay
+ TRIG v(in) VAL='SUPPLY/2' RISE=1
+ TARG v(out) VAL='SUPPLY/2' FALL=1
.measure tp param='(tphl+tplh)/2' * average prop delay
.measure trise * rise time
+ TRIG v(out) VAL='0.1*SUPPLY' RISE=1
+ TARG v(out) VAL='0.9*SUPPLY' RISE=1
.measure tfall * fall time
+ TRIG v(out) VAL='0.9*SUPPLY' FALL=1
+ TARG v(out) VAL='0.1*SUPPLY' FALL=1
.end