import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Define a function for curve fitting (example: polynomial)


# Define different fitting functions
def polynomial(t, a, b, c, d):
    return a * t**3 + b * t**2 + c * t + d  # Cubic polynomial


def exponential(t, a, b, c):
    return a * np.exp(b * t) + c  # Exponential


def power_law(t, a, b, c):
    return a * t**b + c  # Power-law


fitting_function = power_law


# Read data from text file
filename = 'uri.txt'  # Replace with your file path
data = np.loadtxt(filename)

# Split data into time (t) and values (y)
t = data[:, 0]
y = data[:, 1]

# Fit the curve
params, _ = curve_fit(fitting_function, t, y)

# Generate values for the fitted curve
t_fit = np.linspace(min(t), max(t), 500)
y_fit = fitting_function(t_fit, *params)

# Plot the data and the fitted curve
plt.scatter(t, y, label='Data', color='red')
plt.plot(t_fit, y_fit, label='Fitted Curve', color='blue')
plt.xlabel('Time')
plt.ylabel('Value')
plt.legend()
plt.show()

# Print the fitting parameters
print(f'Fitting parameters: a={params[0]}, b={params[1]}, c={params[2]}')
