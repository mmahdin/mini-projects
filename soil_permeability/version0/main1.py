
import Module
import numpy as np
import matplotlib.pyplot as plt

# sigma=True, m=True, K=True, C=True, u=True, U=True
answer = Module.Base().calculate()
list_u = answer[0]
list_U_p = answer[1]
n = answer[2]
m = answer[3]
H = answer[4]
delta_z = answer[5]
delta_t = answer[6]
Tv = answer[7]
q = answer[8]
list_c_v = answer[9]

# devide list_u by list_c
# list_new_u = np.zeros(list_u.shape)
# t = [i*delta_t for i in range(m)]
# print(n)
# for i in range(n):
#     for j in range(m):

#         if not list_c_v[i][j] == 0:
#             list_new_u[i][j] = list_u[i][j] / list_c_v[i][j]
#         else:
#             list_new_u[i][j] = 0

#         if i == 0: list_new_u[i][j] = list_u[i][j]


# for i in list_u.T:
#     print(i, '\n')
# Uav-logt
# Module.plot0(list_U_p, Tv[0])
# u-logt
# Module.plot1(list_u, q, H, delta_t, delta_z, m, n)
# U-log
t = [i*delta_t for i in range(m)]
plt.figure()
plt.plot(t, list_U_p[:-1])
plt.xscale('log')
plt.gca().invert_yaxis()
plt.title("U-t")
plt.xlabel('t')
plt.ylabel('U')
plt.show()
# obj = Module.CurveFit()
# cof = Module.CurveFit.fit(obj, list_new_u,m,n,delta_z,delta_t,H,q)
# print(cof)


# 27/4/1402

# calcutateD = 1
# startTime = 5
# Cvav = np.mean(list_c_v, axis=0)

# if calcutateD:
#     URI = list()
#     UFA = list()

#     t = [i*delta_t for i in range(m)]

#     for t_ in t:
#         URI.append(Module.URI_UFA(t_, Cvav[1], H/2, 1000))
#         UFA.append(Module.URI_UFA(t_, Cvav[-1], H/2, 1000))

#     UNL = list_U_p

#     Module.plt.plot(t, URI)
#     Module.plt.xlabel('t')
#     Module.plt.ylabel('URI')
#     Module.plt.show()

#     Module.plt.plot(t, UFA)
#     Module.plt.xlabel('t')
#     Module.plt.ylabel('UFA')
#     Module.plt.show()

#     D = list()
#     for i in range(startTime, len(URI)):
#         D.append((UNL[i] - URI[i]) / (UFA[i] - URI[i]))

#     with open('hlvhvv.txt', 'w') as file:
#         for item in D:
#             file.write(str(item) + '\n')

#     with open('URI.txt', 'w') as file:
#         for item in URI:
#             file.write(str(item) + '\n')

#     with open('UFA.txt', 'w') as file:
#         for item in UFA:
#             file.write(str(item) + '\n')


# else:
#     D = list()

#     with open('hlvhvv.txt', 'r') as file:
#         for line in file:
#             line = line.strip()

#             try:
#                 item = int(line)
#             except ValueError:
#                 item = float(line)
#             D.append(item)


# t = [i*delta_t for i in range(startTime, m)]


# cof = Module.Cfit(t, D)

# with open('t.txt', 'w') as file:
#     for item in t:
#         file.write(str(item) + '\n')


# Dp = list()
# error = list()
# # newt = [i*delta_t for i in range(startTime, m+500)]
# for t_ in range(len(t)):
#     Dp.append(Module.objective5(t[t_], cof[0], cof[1], cof[2], cof[3], cof[4]))
#     error.append(abs(Dp[t_]-D[t_]))

# with open('Dfit.txt', 'w') as file:
#     for item in Dp:
#         file.write(str(item) + '\n')


# print(cof)
# Module.plt.plot(t, D)
# Module.plt.plot(t, Dp)
# Module.plt.xlabel('t')
# Module.plt.ylabel('D')
# # Module.plt.xscale('log')

# Module.plt.figure()
# Module.plt.plot(t, error)
# # Module.plt.show()
# Module.plt.show()

# URI = list()
# UFA = list()

# t = [i*delta_t for i in range(m)]
# Cvav = np.mean(list_c_v, axis=0)
# print(len(list_U_p))
# print(len(t))
# print(Cvav)
# for t_ in t:
#     URI.append(Module.URI_UFA(t_, Cvav[1], H/2, 1000))
#     UFA.append(Module.URI_UFA(t_, Cvav[-1], H/2, 1000))

# plt.plot(t, URI, label='URI')
# plt.plot(t, list_U_p[:-1], label='list_U_p')
# plt.plot(t, UFA, label='UFA')

# plt.legend()  # Add a legend to display the labels
# plt.show()
