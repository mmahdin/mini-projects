import numpy as np
from numpy import *
import matplotlib.pylab as plt
from scipy.optimize import curve_fit
from scipy.special import gamma


class Base():

    def __init__(self):
        # Get Input
        self.H = float(input('enter H\n'))
        self.T = eval(input('enter T\n'))
        self.n = int(input('enter n\n'))
        self.m = int(eval(input('enter m\n')))
        self.sigma0_prime = float(input('enter sigma 0 prime:\n'))
        self.q = float(input('q \n'))  # delta sigma
        self.Ccn = float(input('enter Ccn\n'))  # cc
        self.Ccr = float(input('enter Ccr\n'))  # cs
        self.e0 = float(input('enter e0:\n'))
        self.kv0 = float(eval(input('enter kv0: \n')))
        self.Ck = float(input('enter Ck\n'))  # M
        self.sigma_c_prime = float(input('enter sigma c prime:\n'))
        self.mv0 = float(input('enter mv0:\n'))
        # self.Kve = float(input('enter Kv\n'))
        # self.sigma_prime_e = float(input('enter sigma prime e\n'))
        # self.k1 = float(input('enter K1\n'))
        # self.K2 = float(input('enter K2\n'))
        # self.ee = float(input('enter ee\n'))
        # Other Data
        self.delta_z = self.H / self.n

        self.delta_t = self.T / self.m

        # self.alpha = 1 - (self.Cc / self.M)

        self.rw = 0.001

        # Initialization The Array
        # np.zeros(self.n + 1)
        self.list_sigma_prime = np.zeros((self.n + 1, self.m + 1))
        for i in range(1, self.n+2):
            self.list_sigma_prime[i -
                                  1][0] = self.sigma0_prime

        self.list_sigma_y = np.zeros((self.n + 1, 1))
        for i in range(self.n+1):
            self.list_sigma_y[i][0] = self.sigma_c_prime

        # self.list_e_0 = np.zeros((self.n + 1, 1))
        # for i in range(self.n+1):
        #     self.list_e_0[i][0] = self.ee + self.Ccn * \
        #         np.log10(self.sigma_prime_e / self.list_sigma_prime[i][0])

        self.list_k_v = np.zeros((self.n + 1, self.m + 1))
        for i in range(self.n+1):
            self.list_k_v[i][0] = self.kv0

        self.list_m_v = np.zeros((self.n + 1, self.m + 1))
        for i in range(self.n+1):
            self.list_m_v[i][0] = self.mv0

        self.list_c_v = np.zeros((self.n + 1, self.m + 1))

        self.list_T_v = np.zeros((self.n + 1, self.m + 1))

        self.list_u = np.zeros((self.n + 1, self.m + 1))
        for i in range(1, self.n):
            self.list_u[i][0] = self.q

        self.list_U = np.zeros((self.n + 1, self.m + 1))

        self.list_U_p = np.zeros(self.m + 1)

    # Main Function
    def calculate(self, Uav_=False, K=False, C=False, u=False, U=False):

        for j in range(1, self.m + 1):

            for i in range(self.n+1):

                self.list_sigma_prime[i][j-1] = self.list_sigma_prime[i][0] + \
                    self.q - self.list_u[i][j-1]
                if self.list_sigma_prime[i][j-1] <= self.sigma_c_prime:
                    # self.list_m_v[i][j] = self.list_m_v[i][0] * \
                    #     (self.list_sigma_prime[i][0] /
                    #      self.list_sigma_prime[i][j-1])
                    self.list_k_v[i][j] = self.list_k_v[i][0] * (
                        self.list_sigma_prime[i][0] / self.list_sigma_prime[i][j-1]) ** (self.Ccn / self.Ck)
                    c = self.Ccn

                else:
                    # self.list_m_v[i][j] = (self.Ccr / self.Ccn) * self.list_m_v[i][0] * (
                    #     self.list_sigma_prime[i][0] / self.list_sigma_prime[i][j-1])
                    self.list_k_v[i][j] = self.list_k_v[i][0] * ((self.list_sigma_prime[i][0] / self.sigma_c_prime) ** (
                        self.Ccn / self.Ck)) * (self.sigma_c_prime / self.list_sigma_prime[i][j-1]) ** (self.Ccr / self.Ck)
                    c = self.Ccr

                # self.list_c_v[i][j] = self.list_k_v[i][j] / \
                #     (self.list_m_v[i][j] * self.rw)
                self.list_c_v[i][j] = self.list_k_v[i][j] * \
                    (self.e0 + 1) * \
                    self.list_sigma_prime[i][j] / (self.rw * 0.434 * c)

                self.list_T_v[i][j] = 4 * self.list_c_v[i][j] * \
                    self.delta_t * j / (self.H**2)

        for j in range(1, self.m+1):
            for i in range(self.n):
                self.list_u[i][j] = ((self.delta_t * self.list_c_v[i][j]) / (self.delta_z ** 2)) \
                    * ((1 + self.list_k_v[i+1][j] / self.list_k_v[i][j]) / (1 + (self.list_k_v[i+1][j] / self.list_k_v[i][j]) * (self.list_c_v[i][j] / self.list_c_v[i+1][j])))\
                    * (((2 * self.list_k_v[i][j] * self.list_u[i-1][j-1]) / (self.list_k_v[i][j] + self.list_k_v[i+1][j]))
                       + ((2 * self.list_k_v[i+1][j] * self.list_u[i+1][j-1]
                           ) / (self.list_k_v[i][j] + self.list_k_v[i+1][j]))
                       - (2 * self.list_u[i][j-1])) \
                    + self.list_u[i][j-1]
                if int(self.list_u[i][0]) != 0:
                    self.list_U[i][j] = 1 - \
                        self.list_u[i][j] / self.list_u[i][0]
                else:
                    self.list_U[i][j] = 0

        for j in range(self.m):
            sum = 0
            for i in range(self.n):
                sum += self.list_u[i][j] * self.delta_z
            self.list_U_p[j] = 1 - sum / (self.q * self.H)

        return self.list_u, self.list_U_p, self.n, self.m, self.H, self.delta_z, self.delta_t, self.list_T_v, self.q, self.list_c_v


class plot0():
    def __init__(self, list_Up, Tv):
        Up = [np.log10(i) for i in list_Up[:-1]]
        # plt.xscale('log')
        plt.plot(np.log10(Tv[:-1]), list_Up[:-1], color='r')
        plt.xlabel('log(Tv)')
        plt.ylabel('Up')
        plt.grid(True, 'both')
        plt.show()


class plot1():
    def __init__(self, u, q, H, delta_t, delta_z, m, n):
        z = [delta_z*i/H for i in range(n+1)]
        t = [i*delta_t for i in range(m)]
        u = u/q
        for j in range(len(t)):
            if 345.5 < t[j] < 346.5 or 458.5 < t[j] < 459.5 or 698.5 < t[j] < 699.5:
                # if 80.9 < t[j] < 81.2 or 149.9 < t[j] < 150.2 or 303.9 < t[j] < 304.2:
                y = u.T[j]
                plt.plot(y[:], z, linestyle='dashed')
        plt.xlabel('u/q')
        plt.ylabel('z/H')
        plt.show()


def fitted():
    return


class CurveFit():
    def objective(self, X, a, b, c, d, e):
        z, t = X
        return d + a*np.sin(b*z + e)*np.exp(-c*t)

    def fit(self, u, m, n, delta_z, delta_t, H, q):
        z = [delta_z*i/H for i in range(n+1)]
        t = [i*delta_t for i in range(m+1)]

        value = list()
        for i in range(n+1):
            for j in range(m+1):
                value.append(u[i][j])
        Z = []
        for i in range(n+1):
            for j in range(m+1):
                Z.append(z[i])

        T = []
        for i in range(n+1):
            for j in range(m+1):
                T.append(t[j])
        T = np.array(T)
        Z = np.array(Z)
        value = np.array(value)
        print('go to cof')
        cof, _ = curve_fit(self.objective, (Z, T), value, maxfev=100000)
        print('end of cof')
        z = [delta_z*i/H for i in range(n+1)]
        t = [i*delta_t for i in range(m)]
        u = u/q
        for j in range(len(t)):
            # if 345.5 < t[j] < 346.5 or 458.5 < t[j] < 459.5 or 698.5 < t[j] < 699.5:
            if 345.5 < t[j] < 346.5:
                pval = []
                for i in range(n+1):
                    pval.append(self.objective(
                        [z[i], t[j]], cof[0], cof[1], cof[2], cof[3], cof[4])/q)

                y = u.T[j]
                plt.plot(y[:], z)
                plt.plot(pval, z)
        plt.xlabel('u/q')
        plt.ylabel('z/H')
        plt.show()
        return cof

# 27/4/1402


def URI_UFA(t, Cv, Hdr, INF):
    s = 0
    Tv = Cv * t / (Hdr**2)
    for m in range(INF):
        M = (2*m+1)*np.pi/2
        s += 2*np.exp(-(M**2)*Tv)/(M**2)
    return 1 - s


def objective(t, a, b, c, d, e):
    return b*t**(1/2) + c*t**2 + d*t + e


def objective2(t, a, b, c, d, e, f, g, h):
    return -a*np.exp(-c*t + b) + d + (e*t + h)/(f*t**(1/2) + g)


def objective3(t, a, b, c, d, e, f):
    return (d/(e + f*np.exp(-a*(t-b))))**c


def gamma_distribution(x, alpha, beta):
    return (beta**alpha)*x**(alpha-1) * np.exp(-beta*x)/gamma(alpha)


def beta(x, a, b):
    return a * (x-a)**(a-1) / (b-a)**a


def objective5(t, a, b, c, d, e):
    return 1/(1 + np.exp(-b*t + c)) - d*np.exp(-a*t)*t**(1/2) - e


def Cfit(t, D):
    if t == 0:
        print('*****************')
    cof, _ = curve_fit(objective5, t, D, maxfev=10000000)
    return cof
