#!/bin/bash

# Define file names
osc_sp="osc.sp"
temp_sp="temp.sp"
result_txt="result.txt"
osc_measure="osc.measure"
temp_measure="temp.measure"

# Define parameters
# x_values=(1 2 3 4 5 6 6.1 6.2 6.3 6.4 6.5 6.6 6.7 6.8 6.9 7 7.1 7.2 7.3 7.4 7.5 7.6 7.7 7.8 7.9 8.1 8.2 8.3 8.5 8.5 8.6 8.7 9 10 11 12 13 14 15)
# B_values=(1)
x1_values=(3 3.5 3.4 4 4.5 4.8 5 5.5 6)
x2_values=(10 11 12 13 14 15 15.5 15.8 16 16.5)


# Loop through x values
for x1 in "${x1_values[@]}"; do
    # Loop through B values
    for x2 in "${x2_values[@]}"; do
        # Calculate W and L values for M6 line
        W_M3=$(awk "BEGIN { printf \"%.2f\", 8 * $x1 }")
        # Calculate W for M5 line
        W_M4=$(awk "BEGIN { printf \"%.2f\", 3 * $x1 }")

        W_M6=$(awk "BEGIN { printf \"%.2f\", 8 * $x2 }")
        # Calculate W for M5 line
        W_M5=$(awk "BEGIN { printf \"%.2f\", 3 * $x2 }")

        # Read osc.sp file and modify W and L values for both M6 and M5 lines
        sed -e "s/W=8\*x1/W=$W_M3/g; s/W=3\*x1/W=$W_M4/g; s/W=8\*x2/W=$W_M6/g; s/W=3\*x2/W=$W_M5/g" "$osc_sp" > "$temp_sp"

        # Run spectre command
        spectre "$temp_sp"

        # Read tp value from temp.measure file
        # tp_value=$(awk '/\btp\b/{print $3}' "$temp_measure")
        tp_value=$(awk '/tp/{print $3}' "$temp_measure")

        # Write x, B, and tp values to result.txt
        echo "$x1 $x2 $tp_value" >> "$result_txt"
    done
done
