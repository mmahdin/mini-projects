library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

-- Define the entity for the test bench
entity FSM_tb is
end FSM_tb;

-- Define the architecture for the test bench
architecture Behavioral of FSM_tb is
    -- Component declaration for the FSM
    component FSM
        Port ( clk : in STD_LOGIC;
               reset : in STD_LOGIC;
               x : in STD_LOGIC;
               z : out STD_LOGIC);
    end component;

    -- Signals to connect to the FSM
    signal clk_tb : STD_LOGIC := '0';
    signal reset_tb : STD_LOGIC := '0';
    signal x_tb : STD_LOGIC := '0';
    signal z_tb : STD_LOGIC;

    -- Clock period definition
    constant clk_period : time := 10 ns;

begin
    -- Instantiate the FSM
    uut: FSM Port Map (
        clk => clk_tb,
        reset => reset_tb,
        x => x_tb,
        z => z_tb
    );

    -- Clock process definitions
    clk_process : process
    begin
        clk_tb <= '0';
        wait for clk_period / 2;
        clk_tb <= '1';
        wait for clk_period / 2;
    end process;

    -- Stimulus process
    stim_proc: process
    begin
        -- Reset the FSM
        reset_tb <= '1';
        wait for clk_period * 2;
        reset_tb <= '0';
        wait for clk_period * 2;

        -- Test sequence
        -- Test state 00
        x_tb <= '0';
        wait for clk_period * 2;  -- Stay in state 00, z should be 0

        x_tb <= '1';
        wait for clk_period * 2;  -- Stay in state 00, z should be 1

        -- Test state 01
        x_tb <= '0';
        wait for clk_period * 2;  -- Move to state 01, z should be 1

        x_tb <= '1';
        wait for clk_period * 2;  -- Move to state 10, z should be 1

        -- Test state 10
        x_tb <= '0';
        wait for clk_period * 
