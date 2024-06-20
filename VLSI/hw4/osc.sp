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
Vin in gnd PULSE 0 'SUPPLY' 10ps 10ps 10ps 2ns 4ns



M1 out1 in gnd gnd nch W=3 L=2
M2 out1 in vdd vdd pch W=8 L=2

M3 out2 out1 gnd gnd nch W=3*x1 L=2
M4 out2 out1 vdd vdd pch W=8*x1 L=2

M5 out3 out2 gnd gnd nch W=3*x2 L=2
M6 out3 out2 vdd vdd pch W=8*x2 L=2

M7 out4 out3 gnd gnd nch W=192 L=2
M8 out4 out3 vdd vdd pch W=512 L=2





*----------------------------------------------------------------------
* Stimulus
*----------------------------------------------------------------------
.tran 0.1ps 4ns
.measure tplh * rising prop delay
+ TRIG v(in) VAL='SUPPLY/2' FALL=1
+ TARG v(out3) VAL='SUPPLY/2' RISE=1
.measure tphl * falling prop delay
+ TRIG v(in) VAL='SUPPLY/2' RISE=1
+ TARG v(out3) VAL='SUPPLY/2' FALL=1
.measure tp param='(tphl+tplh)/2' * average prop delay
.measure trise * rise time
+ TRIG v(out3) VAL='0.1*SUPPLY' RISE=1
+ TARG v(out3) VAL='0.9*SUPPLY' RISE=1
.measure tfall * fall time
+ TRIG v(out3) VAL='0.9*SUPPLY' FALL=1
+ TARG v(out3) VAL='0.1*SUPPLY' FALL=1

.end
