import numpy as np
import matplotlib as plt


class Simulateion:

    def __init__(self):
        self.cv = 0
        self.C = 0
        self.rw = 9.81

        self.dz_list = []
        self.dz_list_up = []

        self.e_list = []
        self.e_list_up = []

    def get_inputs(self):
        self.H = input("enter H:")
        self.T = input("enter T:")
        self.n = input("enter n:")
        self.m = input("enter m:")
        self.sigma0_prime = input("enter sigma0_prime:")
        self.delta_sigma_prime = input("enter delta_sigma_prime:")
        self.CV_RI = input("enter CV(RI):")
        self.CV_FA = input("enter CV(FA):")
        self.Cc = input("enter Cc")
        self.Cs = input("enter Cs")
        self.e0 = input('enter e0')
        self.bk = input('enter bk')
        self.M = input('enter M:')

    def init_matrix(self):
        self.list_u = np.zeros((self.n, self.m))
        self.list_u[1:-1, 0] = self.delta_sigma_prime
        a = self.calc_a(self.delta_z0, self.CV_RI)
        cv = self.delta_sigma_prime
        for j in range(1, self.n):
            self.list_u[j, 1] = a*cv + a*cv + (1-a-a)*cv

        # self.list_Cv = np.zeros((self.n, self.m))
        # self.list_Cv[:, 0] = self.CV_RI

        # self.list_sigma_prime = np.zeros((self.n, self.m))
        # self.list_sigma_prime = self.sigma0_prime + self.delta_sigma_prime - self.list_u

        self.delta_z0 = self.H / self.n

        self.delta_t = self.T / self.m

        self.dz_list = [self.delta_z0 for _ in range(self.n)]

        self.e_list = [self.e0 for _ in range(self.n)]

    def run(self):
        for j in range(1, self.m+1):
            for i in range(1, self.n+1):
                if self.sig_avg(i-1, j) >= self.sig_avg(i-1, j-1):
                    self.C = self.Cc
                else:
                    self.C = self.Cs

                self.calc_u(i, j)

            self.dz_list = self.dz_list_up
            self.dz_list_up = []

            self.e_list = self.e_list_up
            self.e_list_up = []

    def calc_sigma_prime(self, i, j):
        return self.sigma0_prime + self.delta_sigma_prime - self.list_u[i, j]

    def sig_avg(self, i, j):
        return self.calc_sigma_prime(i, j) + self.calc_sigma_prime(i, j)

    def calc_e(self, i, j):
        sigp = self.calc_sigma_prime()
        avgp = self.sig_avg(i, j)
        avgn = self.sig_avg(i, j-1)
        en = self.e_list[i]
        if avgp >= avgn:
            e = en - self.Cc * np.log10(avgp/avgn)
            self.e_list_up.append(e)
            return e
        else:
            e = en - self.Cs * np.log10(avgp/avgn)
            self.e_list_up.append(e)
            return e

    def calc_dz(self, i, j):
        prev_dz = self.dz_list[i]
        ep = self.calc_e(i, j)
        en = self.calc_e(i, j-1)
        dz = prev_dz * (1 - (ep - en)/(1 + ep))
        self.dz_list_up[i] = dz
        return dz

    def calc_cv(self, i, j):
        sigma = self.sig_avg(i, j)
        return 2.3*(1+self.e0) * (10**((self.e0-self.bk)/self.M)) * (sigma**(1-self.C/self.M)) / (self.rw*self.Cc)

    def calc_a(self, i, j):
        cv = self.calc_cv(i, j)
        dz = self.calc_dz(i, j)
        return cv*self.delta_t / (dz**2)

    def calc_u(self, i, j):
        an = self.calc_a(i-1, j)
        ap = self.calc_a(i+1, j)
        self.list_u[i, j+1] = an*self.list_u[i-1, j] + ap * \
            self.list_u[i+1, j] + (1-an-ap)*self.list_u[i, j]
