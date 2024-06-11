GHDL=ghdl
FLAGS="--std=08"

all:
	$(GHDL) -a  test.vhd test_tb.vhd
	$(GHDL) -e  fsm 
	$(GHDL) -r  fsm --wave=wave.ghw --stop-time=1us