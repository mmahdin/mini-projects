import re
import subprocess
import os
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import time

# Define parameters

def generate_spice(wp_value, wn_value, file, out=0):
    # Read the input file
    with open(file, 'r') as file:
        content = file.read()

    # Replace wp and wn with their respective values
    content = content.replace('wp', str(wp_value))
    content = content.replace('wn', str(wn_value))

    # Function to evaluate expressions
    def evaluate_expression(expression):
        try:
            return str(eval(expression))
        except Exception as e:
            return expression

    # Replace AS, PS, AD, PD values with their evaluated expressions
    pattern = re.compile(r"(AS|PS|AD|PD)='([^']*)'")
    content = pattern.sub(lambda match: f"{match.group(1)}={evaluate_expression(match.group(2))}", content)

    # Write the output to temp.sp
    with open('temp.sp', 'w') as file:
        file.write(content)

    # Run the ngspice command
    if out:
        subprocess.run(['ngspice', '-b', '-r', 'temp.out', '-o', 'temp.log', 'temp.sp'])
    else:
        subprocess.run(['ngspice', '-b', '-o', 'temp.log', 'temp.sp'])
    time.sleep(0.5)

def sweep(wp_value, wn_value, file):
    generate_spice(wp_value, wn_value, file)

    # Read the temp.log file and extract tphl, tplh, and tp values
    tphl = tplh = tp = None

    with open('temp.log', 'r') as file:
        for line in file:
            if 'tphl' in line or 'tplh' in line or 'tp' in line:
                parts = line.split('=')
                if len(parts) > 1:
                    value = parts[1].split()[0]
                    if 'tphl' in line:
                        tphl = float(value)
                    elif 'tplh' in line:
                        tplh = float(value)
                    elif 'tp' in line:
                        tp = float(value)

    # Print the extracted values
    # print(f"tphl={tphl}")
    # print(f"tplh={tplh}")
    # print(f"tp={tp}")

    # Delete the temp.log file
    os.remove('temp.log')

    return [tphl, tplh, tp]

def w2f(hl,lh,tp):
    with open('tphl', 'w') as f:
        for item in hl:
            f.write(str(item) + '\n')
    with open('tplh', 'w') as f:
        for item in lh:
            f.write(str(item) + '\n')
    with open('tp', 'w') as f:
        for item in tp:
            f.write(str(item) + '\n')

def readList():
    with open('tphl', 'r') as f:
        tphl = [line.strip() for line in f.readlines()]
    with open('tplh', 'r') as f:
        tplh = [line.strip() for line in f.readlines()]
    with open('tp', 'r') as f:
        tp = [line.strip() for line in f.readlines()]
    
    return [tphl, tplh, tp]

def heat_plot(wp, wn, data, t):
    x_values = []
    y_values = []
    z_values = []
    cnt = 0
    for i in wp:
        for j in wn:
            if data[cnt] != "None":
                x_values.append(i)
                y_values.append(j)
                z_values.append(float(data[cnt]))
            cnt += 1

    x_unique = sorted(list(set(x_values)))
    y_unique = sorted(list(set(y_values)))

    # Create a grid of z values
    z_grid = np.zeros((len(y_unique), len(x_unique)))
    for x, y, z in zip(x_values, y_values, z_values):
        z_grid[y_unique.index(y), x_unique.index(x)] = z

    plt.imshow(z_grid, extent=[min(x_unique), max(x_unique), min(y_unique), max(y_unique)],
               cmap='viridis', aspect='auto', origin='lower')
    plt.colorbar(label='Third Row Values')
    plt.xlabel('wp')
    plt.ylabel('wn')
    plt.title(t)
    plt.show()


wp_list = [i for i in range(1, 50)]
wn_list = [i for i in range(1, 50)]

tphl_list = []
tplh_list = []
tp_list = []

generate = False

if not generate:
    tphl_list, tplh_list, tp_list = readList()
else:
    cnt = 1
    for wp in wp_list:
        for wn in wn_list:
            print(f"attempt {cnt}..")
            try:
                res = sweep(wp, wn, 'testgt')
                tphl_list.append(res[0])
                tplh_list.append(res[1])
                tp_list.append(res[2])
            except:
                pass
            if cnt%50==0:
                # w2f(tphl_list, tplh_list, tp_list)
                pass
            cnt += 1

if generate:
    w2f(tphl_list, tplh_list, tp_list)

# heat_plot(wp_list, wn_list, tphl_list, 'tphl')
# heat_plot(wp_list, wn_list, tplh_list, 'tplh')
# heat_plot(wp_list, wn_list, tp_list, 'tp')

# generate_spice(4, 4, 'testtg')