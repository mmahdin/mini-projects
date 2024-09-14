import numpy as np
import matplotlib.pyplot as plt


class Simulateion:

    def __init__(self):
        self.cv = 0
        self.C = 0
        self.rw = 0.001

        self.dz_list = []
        self.dz_list_up = []

        self.e_list = []
        self.e_list_up = []

        self.file = open('temp.txt', 'w')

    def get_inputs(self):
        self.H = float(input("enter H:"))
        self.T = int(input("enter T:"))
        self.n = int(input("enter n:"))
        self.m = int(input("enter m:"))
        self.sigma0_prime = float(input("enter sigma0_prime:"))
        self.delta_sigma_prime = float(input("enter delta_sigma_prime:"))
        self.Cc = float(input("enter Cc"))
        self.Cs = float(input("enter Cs"))
        self.e0 = float(input('enter e0'))
        self.bk = float(eval(input('enter bk')))
        self.M = float(input('enter M:'))
        print('***************', ' ', self.bk)

    def init_matrix(self):
        self.delta_z0 = self.H / self.n
        self.delta_t = self.T / self.m

        self.CV_RI = 2.3*(1+self.e0) * (10**((self.e0-self.bk)/self.M)) * \
            (self.sigma0_prime**(1-self.C/self.M)) / (self.rw*self.Cc)
        self.CV_FA = 2.3*(1+self.e0) * (10**((self.e0-self.bk)/self.M)) * (
            (self.sigma0_prime+self.delta_sigma_prime)**(1-self.C/self.M)) / (self.rw*self.Cc)

        self.list_u = np.zeros((self.n, self.m))
        self.list_u[1:-1, 0] = self.delta_sigma_prime
        self.calc_c(1, 1)
        cv = self.delta_sigma_prime
        a = cv*self.delta_t / (self.delta_z0**2)
        for j in range(1, self.n-1):
            self.list_u[j, 1] = a*cv + a*cv + (1-a-a)*cv

        self.e_list = [self.e0 for _ in range(self.n)]

        self.list_delta_z = np.zeros_like(self.list_u)
        self.list_delta_z[:, 0] = self.delta_z0

    def run(self):
        self.file.write('j: 0' + '\n')
        for qq in self.list_u[:, 0]:
            self.file.write(str(qq) + ', ')
        self.file.write('\n')

        self.file.write('j: 1' + '\n')
        for qq in self.list_u[:, 1]:
            self.file.write(str(qq) + ', ')
        self.file.write('\n')

        for j in range(1, self.m-1):
            for i in range(1, self.n-2):
                self.calc_c(i, j)

                self.file.write('i: ' + str(i) + '    j: ' + str(j) + '\n')

                self.calc_u(i, j)

                if np.isnan(self.list_u[i, j]):
                    self.file.close()
                    break
            if np.isnan(self.list_u[i, j]):
                break

            for qq in self.list_u[:, j+1]:
                self.file.write(str(qq) + ', ')
            self.file.write('\n')
            self.file.write('**********\n')

            self.e_list = self.e_list_up
            self.e_list_up = []
        np.savetxt('dz', self.list_delta_z, fmt='%.2f', delimiter=',')

    def calc_sigma_prime(self, i, j):
        return self.sigma0_prime + self.delta_sigma_prime - self.list_u[i, j]

    def sig_avg(self, i, j):
        # print('sig_avg', i, j)
        return (self.calc_sigma_prime(i+1, j) + self.calc_sigma_prime(i, j))/2

    def calc_e(self, i, j):
        # print('calc_e', i, j)
        if j == 0:
            return self.e0
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
        # print('calc_dz', i, j)
        ep = self.calc_e(i, j)
        en = self.calc_e(i, j-1)
        dz = self.list_delta_z[i, j-1] * (1 - (ep - en)/(1 + ep))
        self.list_delta_z[i, j] = dz
        return dz

    def calc_cv(self, i, j):
        # print('calc_cv', i, j)
        sigma = self.sig_avg(i, j)
        self.file.write(f"u[{i-1},{j}]: " +
                        str(self.list_u[i-1, j]) + '  ***  ')
        self.file.write(f"u[{i},{j}]: " + str(self.list_u[i, j]) + '  ***  ')
        self.file.write("sigma: " + str(sigma) + '  ***')
        self.file.write('pow: ' + str((1-self.C/self.M)) + '  ***  ')
        self.file.write("sigma2pow: " +
                        str((sigma**(1-self.C/self.M))) + '  ***  ')
        self.file.write("div: " + str((self.rw*self.Cc)) + '  ***  ')
        self.file.write(
            "10pow: " + str(10**((self.e0-self.bk)/self.M)) + '  ***  ')
        self.file.write("cv: " + str(2.3*(1+self.e0) * (10**((self.e0-self.bk)/self.M))
                        * (sigma**(1-self.C/self.M)) / (self.rw*self.Cc)) + '  ***  ')
        return 2.3*(1+self.e0) * (10**((self.e0-self.bk)/self.M)) * (sigma**(1-self.C/self.M)) / (self.rw*self.Cc)

    def calc_c(self, i, j):
        if self.sig_avg(i-1, j) >= self.sig_avg(i-1, j-1):
            self.C = self.Cc
        else:
            self.C = self.Cs

    def calc_a(self, i, j):
        # print('calc_a', i, j)
        cv = self.calc_cv(i, j)
        dz = self.calc_dz(i, j)
        self.file.write('dz: ' + str(dz) + '  ***  ' + 'a: ' +
                        str(cv*self.delta_t / (dz**2)) + '\n')
        return cv*self.delta_t / (dz**2)

    def calc_u(self, i, j):
        an = self.calc_a(i-1, j)
        ap = self.calc_a(i+1, j)
        self.list_u[i, j+1] = (an*self.list_u[i-1, j] + ap *
                               self.list_u[i+1, j] + (1-an-ap)*self.list_u[i, j])/1

    def URI_UFA(self, t, Cv, Hdr, INF):
        s = 0
        Tv = Cv * t / (Hdr**2)
        for m in range(INF):
            M = (2*m+1)*np.pi/2
            s += 2*np.exp(-(M**2)*Tv)/(M**2)
        return 1 - s

    def calc_URI_UFA(self):
        # print("calc URI UFA")
        URI = list()
        UFA = list()

        t = [i*self.delta_t for i in range(self.m)]
        for t_ in t:
            URI.append(self.URI_UFA(t_, self.Cc, self.H/2, 1000))
            UFA.append(self.URI_UFA(t_, self.Cs, self.H/2, 1000))

        return URI, UFA, t

    def calc_D(self, uri, ufa, unl):
        startTime = 0
        D = list()
        for i in range(startTime, len(uri)):
            D.append((unl[i] - uri[i]) / (ufa[i] - uri[i]))
        return D

    def calc_UNL(self):
        # print("calc UNL")
        UNL = []
        for j in range(self.m):
            sum = 0
            for i in range(1, self.n):
                sum += self.list_u[i][j] * self.list_delta_z[i, j]
            UNL.append(1 - sum / (self.delta_sigma_prime * self.H))
        return UNL

    def plot(self):
        print('\n----- plot -----')
        print(self.list_u)
        uri, ufa, t = self.calc_URI_UFA()
        unl = self.calc_UNL()
        D = self.calc_D(uri, ufa, unl)
        TvRI = self.CV_RI * np.array(t) / self.H

        plt.figure()
        plt.plot(t[:-1], unl[:-1])
        plt.xscale('log')
        plt.gca().invert_yaxis()
        plt.title("Unl-t")
        plt.xlabel('t')
        plt.ylabel('Unl')
        plt.show()

        plt.figure()
        plt.plot(t[:-1], uri[:-1])
        plt.xscale('log')
        plt.gca().invert_yaxis()
        plt.title("URI-t")
        plt.xlabel('t')
        plt.ylabel('URI')
        plt.show()

        plt.figure()
        plt.plot(t[:-1], ufa[:-1])
        plt.xscale('log')
        plt.gca().invert_yaxis()
        plt.title("UFA-t")
        plt.xlabel('t')
        plt.ylabel('UFA')
        plt.show()

        plt.figure()
        plt.plot(t[:-1], D[:-1])
        plt.title("D-t")
        plt.xlabel('t')
        plt.ylabel('D')
        plt.show()

        plt.figure()
        plt.plot(TvRI[1:], D[1:])
        plt.title("D-TvRI")
        plt.xlabel('TvRI')
        plt.ylabel('D')
        plt.show()


if __name__ == "__main__":
    sim = Simulateion()
    sim.get_inputs()
    sim.init_matrix()
    sim.run()
    sim.plot()
