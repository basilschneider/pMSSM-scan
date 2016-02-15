#!/usr/bin/env python2

""" Mass scan. """

from MassScan import MassScan

if __name__ == "__main__":
    MY_SCAN = MassScan()
    MY_SCAN.set_threshold(1.)
    L_COORDINATES = [50*i for i in range(5, 8)]
    M_3 = [250*i for i in range(1, 4)]
    MU_EWSB = [250*i for i in range(1, 3)]
    MY_SCAN.l_m_3 = M_3
    MY_SCAN.l_mu_ewsb = MU_EWSB
    PLOTS = MY_SCAN.do_scan()
    PLOTS.set_rootfile('histos.root')
    PLOTS.set_directory("test12")
    #PLOTS.set_star(-1071.46632, 534.761347)
    PLOTS.plot()
