library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

-- Define the entity
entity FSM is
    Port ( clk : in STD_LOGIC;          -- Clock input
           reset : in STD_LOGIC;        -- Reset input
           x : in STD_LOGIC;            -- Input x
           z : out STD_LOGIC);          -- Output z
end FSM;

-- Define the architecture
architecture Behavioral of FSM is
    -- Define state type
    type state_type is (S00, S01, S10, S11);
    signal state, next_state : state_type;

begin
    -- Process for state transitions
    process (clk, reset)
    begin
        if reset = '1' then
            state <= S00;               -- Reset state to S00
        elsif rising_edge(clk) then
            state <= next_state;        -- Update state on clock edge
        end if;
    end process;

    -- Process for next state logic and output logic
    process (state, x)
    begin
        case state is
            when S00 =>
                if x = '0' then
                    next_state <= S00;
                    z <= '0';
                else
                    next_state <= S00;
                    z <= '1';
                end if;
            when S01 =>
                if x = '0' then
                    next_state <= S00;
                    z <= '1';
                else
                    next_state <= S10;
                    z <= '1';
                end if;
            when S10 =>
                if x = '0' then
                    next_state <= S01;
                    z <= '0';
                else
                    next_state <= S11;
                    z <= '1';
                end if;
            when S11 =>
                if x = '0' then
                    next_state <= S11;
                    z <= '1';
                else
                    next_state <= S11;
                    z <= '1';
                end if;
            when others =>
                next_state <= S00;      -- Default state
                z <= '0';
        end case;
    end process;
end Behavioral;
