import numpy as np
import matplotlib.pyplot as plt
from main import generate_spice

def parse_file(file_path, variable_index):
    time_values = []
    variable_values = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Find the number of variables
    num_variables = 0
    for line in lines:
        if line.startswith('No. Variables:'):
            num_variables = int(line.split(':')[1].strip())
            break

    # Find the starting point of Values section
    values_index = 0
    for i, line in enumerate(lines):
        if line.startswith('Values:'):
            values_index = i + 1
            break

    # Iterate through each epoch to extract the time value and the value of the specified variable
    epoch_length = num_variables  # Including the index line
    for i in range(values_index, len(lines), epoch_length):
        epoch_data = lines[i:i+epoch_length]  # Read the epoch
        if len(epoch_data) < epoch_length:
            continue
        
        # Extract the time value from the second item in the first line of the epoch
        time_value = float(epoch_data[0].split()[1])
        
        # Extract the specified variable value
        variable_value = float(epoch_data[variable_index].strip())
        
        time_values.append(time_value)
        variable_values.append(variable_value)

    # Convert lists to numpy arrays
    time_values = np.array(time_values)
    variable_values = np.array(variable_values)

    return time_values, variable_values

def plot_values(time_values, variable_values, variable_name):
    plt.figure(figsize=(10, 6))
    for i in range(len(variable_values)):
        plt.plot(time_values, variable_values[i], label=variable_name[i])
    plt.xlabel('Time (s)')
    plt.ylabel(variable_name)
    plt.title(f'{variable_name} vs Time')
    plt.legend()
    plt.grid(True)
    plt.show()
    
def indexOfMean(input, output, time, mean, up, down, t=10**(-9)):
    rise_input_list = []
    rise_output_list = []
    fall_input_list = []
    fall_output_list = []
    rise20p_list = []
    rise90p_list = []
    fall90p_list = []
    fall20p_list = []
    for i in range(1, len(input)-1):
        if time[i] > t:
            if input[i-1] < mean and input[i+1] >= mean:
                rise_input_list.append(time[i])
            if input[i-1] > mean and input[i+1] <= mean:
                fall_input_list.append(time[i])
    for i in range(1, len(output)-1):
        if time[i] > t:
            if output[i-1] < mean and output[i+1] >= mean:
                rise_output_list.append(time[i])
            if output[i-1] > mean and output[i+1] <= mean:
                fall_output_list.append(time[i])

            if output[i-1] < down and output[i+1] >= down:
                rise20p_list.append(time[i])
            if output[i-1] < up and output[i+1] >= up:
                rise90p_list.append(time[i])
            
            if output[i-1] > up and output[i+1] <= up:
                fall90p_list.append(time[i])
            if output[i-1] > down and output[i+1] <= down:
                fall20p_list.append(time[i])
    # print('************************')
    # print(rise_input_list)
    # print(fall_input_list)
    # print(rise_output_list)
    # print(fall_output_list)
    # print('************************')
    rising_edge = [rise90p_list[i] - rise20p_list[i] for i in range(len(rise20p_list))]
    falling_edge = [fall20p_list[i] - fall90p_list[i] for i in range(len(fall90p_list))]
    tphl = [fall_output_list[i] - rise_input_list[i] for i in range(min(len(rise_input_list), len(fall_output_list)))]
    tplh = [rise_output_list[i] - fall_input_list[i] for i in range(min(len(rise_output_list), len(fall_input_list)))]
    tp = [(tphl[i] + tplh[i])/2 for i in range(min(len(tphl), len(tplh)))]
    
    return [rising_edge, falling_edge, tphl, tplh, tp]


# Specify the file path and variable index
file_path = 'temp.out'
MAX = 1.8
MIN = 0
MEAN = (MAX+MIN)/2
L = (MAX-MIN)

test = 'testcmos'

generate_spice(6, 3, test, 1)

if test == 'testcmos':
    index_out = 10
    index_s = 7
else:
    index_out = 7
    index_s = 3



time_values, out = parse_file(file_path, index_out)
variable_name = 'v(out)'  # Provide the variable name for labeling the plot


time_values, s = parse_file(file_path, index_s)
variable_name = 'v(s)'  # Provide the variable name for labeling the plot

[rising_edge, falling_edge, tphl, tplh, tp] = indexOfMean(s, out, time_values, MEAN, 0.9*L, 0.1*L)

print('------------------------------------------------')
print("Rising Edge:")
print(rising_edge)
print('\n------------------------------------------------')
print("Falling Edge:")
print(falling_edge)
print('\n------------------------------------------------')
print("tphl:")
print(tphl)
print('\n------------------------------------------------')
print("tplh:")
print(tplh)
print('\n------------------------------------------------')
print("tp:")
print(tp)
print('\n------------------------------------------------')
plot_values(time_values, [out, s], ['out', 'sel'])


