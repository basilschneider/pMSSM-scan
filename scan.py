#!/usr/bin/env python2

""" Mass scan. """

from MassScan import MassScan

if __name__ == "__main__":
    MY_SCAN = MassScan()
    MY_SCAN.set_threshold(.01)
    L_COORDINATES = [50*i for i in range(5, 8)]
    M_3 = [100*i for i in range(1, 10)]
    MU_EWSB = [100*i for i in range(1, 10)]
    MY_SCAN.l_prmtr_x = [400]
    MY_SCAN.l_prmtr_y = [300]
    PLOTS = MY_SCAN.do_scan()
    PLOTS.set_axis('M_{3} [GeV]', '#mu [GeV]')
    PLOTS.set_rootfile('histos.root')
    PLOTS.set_directory('output7/')
    #PLOTS.set_star(-1071.46632, 534.761347)
    PLOTS.plot()
