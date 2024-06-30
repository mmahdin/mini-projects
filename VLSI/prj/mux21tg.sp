
.option scale=90n
.lib rf018.l TT
.param SUPPLY=1.8v

vdd VDD gnd SUPPLY

m1   B S out gnd nch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

m2   out nS B VDD pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26


m3   A nS out gnd nch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26

m4   out S A VDD pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26


m5 nS S VDD VDD pch W=6 L=2
+ AS=20 PS=18 AD=20 PD=18
m6 nS S gnd gnd nch W=3 L=2
+ AS=10 PS=14 AD=10 PD=14


C1 out 0 20fF

vins0 S gnd dc 0 pulse ('SUPPLY' 0 1n 0.1n 0.1n 2n 4n)
vina  A gnd dc 0 pulse ('SUPPLY' 0 8n 0 0 10n 20n)
vinb  B gnd dc 0 pulse ('SUPPLY' 0 0 0 0 20 20n)
* vins1 4 gnd dc 0 pulse (0 3 0 0.1u 0.1u 40u 80u)


.tran 0.1p 8n
.print v(out) v(S) v(nS) v(A) v(B)

.control 
tran 1p 4n
plot v(A)
plot v(B)
plot v(S)
plot v(out)
.endc     


.measure tran tphl TRIG V(S) VAL='SUPPLY/2' RISE=1 TARG V(out) VAL='SUPPLY/2' FALL=1
.measure tran tplh TRIG V(S) VAL='SUPPLY/2' FALL=1 TARG V(out) VAL='SUPPLY/2' RISE=1
.measure tran tp PARAM='(tphl + tplh) / 2'

* .print tp

.control
  run
  set filetype=ascii
.endc


.end