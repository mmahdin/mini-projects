import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def filter_file(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    filtered_lines = [line.strip() for line in lines if len(line.split()) == 3]

    with open(output_file, 'w') as f:
        f.write('\n'.join(filtered_lines))



# def plot_data(input_file):
#     x_values = []
#     z_values = []

#     with open(input_file, 'r') as f:
#         for line in f:
#             values = line.split()
#             if len(values) == 3:
#                 x_values.append(float(values[0]))
#                 z_values.append(float(values[2]))
#     min_y_index = z_values.index(min(z_values))
#     min_x_value = x_values[min_y_index]
#     print("Minimum y:", min(z_values))
#     print("Related x:", min_x_value)
#     plt.plot(x_values, z_values, marker='o', linestyle='-')
#     plt.xlabel('x')
#     plt.ylabel('tp')
#     plt.title('tp-x')
#     plt.grid(True)
#     plt.show()

def plot_data(input_file):
    x_values = []
    y_values = []
    z_values = []

    with open(input_file, 'r') as f:
        for line in f:
            values = line.split()
            if len(values) == 3:
                x_values.append(float(values[0]))
                y_values.append(float(values[1]))
                z_values.append(float(values[2]))

    x_unique = sorted(list(set(x_values)))
    y_unique = sorted(list(set(y_values)))

    # Find the index of the minimum value in z
    min_z_index = z_values.index(min(z_values))

    # Get the corresponding values of x and y using the index
    min_x_value = x_values[min_z_index]
    min_y_value = y_values[min_z_index]
    min_z_value = z_values[min_z_index]

    print("Minimum tp:", min_z_value)
    print("Related x1:", min_x_value)
    print("Related x2:", min_y_value)

    # Create a grid of z values
    z_grid = np.zeros((len(y_unique), len(x_unique)))
    for x, y, z in zip(x_values, y_values, z_values):
        z_grid[y_unique.index(y), x_unique.index(x)] = z

    plt.imshow(z_grid, extent=[min(x_unique), max(x_unique), min(y_unique), max(y_unique)],
               cmap='viridis', aspect='auto', origin='lower')
    plt.colorbar(label='Third Row Values')
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.title('tp vs x1 and x2 ')
    plt.show()


input_file = "result.txt"  # Replace "input.txt" with the path to your input file
output_file = "clean_result.txt"  # Replace "output.txt" with the desired output file name
filter_file(input_file, output_file)
input_file = "clean_result.txt"  # Replace "input.txt" with the path to your input file
plot_data(input_file)

