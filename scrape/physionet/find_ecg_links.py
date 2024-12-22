
with open('devices.txt', 'r') as f:
    lines = f.readlines()

new_data = []
for line in lines:
    new_data.append(line.replace('@\n', ''))

with open('devices.txt', 'w') as f:
    for line in new_data:
        f.write(line)

# idxs = []
# idx = 0
# for line in lines:
#     if 'ecg' in line.strip().lower():
#         idxs.append(idx)
#     idx += 1

# print(idxs)
