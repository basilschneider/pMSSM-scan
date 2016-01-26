#!/usr/bin/env python2

""" Mass scan. """

from MassScan import MassScan

if __name__ == "__main__":
    MY_SCAN = MassScan()
    MY_SCAN.set_threshold(1e-1)
    L_COORDINATES = [50*i for i in range(5, 8)]
    M_3 = [250*i for i in range(-6, 15)]
    MU_EWSB = [100*i for i in range(1, 16)]
    MY_SCAN.l_m_3 = [100, 200]
    MY_SCAN.l_mu_ewsb = [300, 400]
    PLOTS = MY_SCAN.do_scan()
    PLOTS.set_rootfile('histos.root')
    PLOTS.set_directory('test04')
    PLOTS.plot()
