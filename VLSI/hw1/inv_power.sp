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
Vin in gnd PULSE 0 'SUPPLY' 0ps 10ps 10ps 5ns 10ns
M1 out in gnd gnd nch W=4 L=2
+ AS=20 PS=18 AD=20 PD=18
M2 out in vdd vdd pch W=8 L=2
+ AS=40 PS=26 AD=40 PD=26
C1 out 0 20fF
*----------------------------------------------------------------------
* Stimulus
*----------------------------------------------------------------------
.tran 0.1ps 10ns
.measure tran EVOH integ par('i(Vdd)*v(Vdd)') from 0 to 5.0ns
.measure tran EVOL integ par('i(Vdd)*v(Vdd)') from 5.0ns to 10ns
.measure tran Ptotal integ par('i(Vdd)*v(Vdd)/10n') from 0 to 10ns
.measure tran PstatVOL integ par('i(Vdd)*v(Vdd)/4n') from 1n to 5ns
.measure tran PstatVOH integ par('i(Vdd)*v(Vdd)/4n') from 6n to 10ns
.measure Pstatic param='(PstatVOH+PstatVOL)/2' * average static power

.end