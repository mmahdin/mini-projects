
.param SUPPLY=1.8

Vin in gnd PULSE 0 'SUPPLY' delay=100p trise=100p

C1 in gnd 0.1p
L1 in 1 2n
R1 1 2 6.67

C2 2 gnd 0.2p
L2 2 3 2n
R2 3 4 6.67

C3 4 gnd 0.4p
L3 4 5 2n
R3 5 6 6.67

C4 6 gnd 0.4p
L4 6 7 2n
R4 7 8 6.67

C5 8 gnd 0.2p
L5 8 9 2n
R5 9 out 6.67

C6 out gnd 2.1p


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