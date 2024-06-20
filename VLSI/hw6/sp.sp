.param SUPPLY=2.5
.option scale=90n
.lib 'rf018.l' TT
.temp 7

* SPICE code for the given circuit
Vdd VDD gnd 2.5
VIN A 0 PULSE(2.5 0 0 50p 50p 1000p 2000p)
VB B 0 2.5

* NMOS Transistor M_n
Mn A B X 0 nch W=4 L=2

* PMOS Transistor M_r
Mr X out VDD VDD pch W=16 L=2

* PMOS Transistor M_2
M2 out X VDD VDD pch W=12 L=2

* NMOS Transistor M_1
M1 out X 0 0 nch W=4 L=2

* Initial condition 
.ic V(X)=2.5V

*----------------------------------------------------------------------
* Stimulus
*----------------------------------------------------------------------
.tran 0.1ps 4ns

.end
