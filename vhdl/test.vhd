-- FSM VHDL code based on the provided state transition table

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Entity declaration for FSM
entity FSM is
    Port (
        clk     : in  STD_LOGIC;   -- Clock signal
        reset   : in  STD_LOGIC;   -- Reset signal
        a       : in  STD_LOGIC;   -- Input bit a
        b       : in  STD_LOGIC;   -- Input bit b
        x       : in  STD_LOGIC;   -- Input bit x
        z       : out STD_LOGIC;   -- Output bit z
        next_a  : out STD_LOGIC;   -- Output bit a for next state
        next_b  : out STD_LOGIC    -- Output bit b for next state
    );
end FSM;

-- Architecture declaration for FSM
architecture Behavioral of FSM is
    -- State type definition
    type state_type is (S000, S001, S010, S011, S100, S101, S110, S111);
    signal current_state, next_state : state_type;
begin

    -- Sequential process to update the current state on clock edge
    process (clk, reset)
    begin
        if reset = '1' then
            current_state <= S000;  -- Initialize to state S000 on reset
        elsif rising_edge(clk) then
            current_state <= next_state;  -- Update state on clock edge
        end if;
    end process;

    -- Combinatorial process to determine next state and outputs
    process (current_state, a, b, x)
    begin
        case current_state is
            when S000 =>
                if (a = '0' and b = '0' and x = '0') then
                    next_state <= S000;
                    next_a <= '0'; next_b <= '0'; z <= '0';
                end if;
                
            when S001 =>
                if (a = '0' and b = '0' and x = '1') then
                    next_state <= S001;
                    next_a <= '0'; next_b <= '0'; z <= '1';
                elsif (a = '0' and b = '1' and x = '0') then
                    next_state <= S001;
                    next_a <= '0'; next_b <= '0'; z <= '1';
                end if;
                
            when S010 =>
                if (a = '1' and b = '0' and x = '0') then
                    next_state <= S010;
                    next_a <= '0'; next_b <= '1'; z <= '0';
                end if;

            when S011 =>
                if (a = '0' and b = '1' and x = '1') then
                    next_state <= S011;
                    next_a <= '1'; next_b <= '0'; z <= '1';
                end if;

            when S100 =>
                if (a = '1' and b = '0' and x = '0') then
                    next_state <= S010;
                    next_a <= '0'; next_b <= '1'; z <= '0';
                end if;

            when S101 =>
                if (a = '1' and b = '0' and x = '1') then
                    next_state <= S111;
                    next_a <= '1'; next_b <= '1'; z <= '1';
                end if;

            when S110 =>
                if (a = '1' and b = '1' and x = '0') then
                    next_state <= S111;
                    next_a <= '1'; next_b <= '1'; z <= '1';
                end if;

            when S111 =>
                if (a = '1' and b = '1' and x = '1') then
                    next_state <= S111;
                    next_a <= '1'; next_b <= '1'; z <= '1';
                end if;

            when others =>
                next_state <= S000;
                next_a <= '0'; next_b <= '0'; z <= '0';

        end case;
    end process;

end Behavioral;
