import matplotlib.pyplot as plt


x = [1,6,8,2,7,4,5,2]
y = [2,3,4,5,5,6,7,8]
labels = ['A1','A2','A3','A4', 'A5','A6','A7','A8']

plt.scatter(x, y)
for i, label in enumerate(labels):
    plt.annotate(label, (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')

cx = [3.67, 7, 1.5]
cy = [7, 4, 3.5]

for j in range(3):
    print(f'Distance to C{j+1}')
    for i in range(len(x)):
        res = ((x[i]-cx[j])**2 + (y[i]-cy[j])**2)**0.5
        print(f'A{i+1}: ', res)

plt.show()