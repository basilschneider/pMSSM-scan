#!/usr/bin/env python2

""" Mass scan. """

from MassScan import MassScan

if __name__ == "__main__":
    MY_SCAN = MassScan()
    MY_SCAN.set_threshold(.01)
    MY_SCAN.set_parameter(3, 23)
    MY_SCAN.set_parameter_add_y(1, 100)
    M_3 = [100*i for i in range(1, 10)]
    MU_EWSB = [100*i for i in range(1, 10)]
    MY_SCAN.l_prmtr_x = [400]
    MY_SCAN.l_prmtr_y = [600]
    PLOTS = MY_SCAN.do_scan()
    PLOTS.set_rootfile('histos.root')
    PLOTS.set_directory('output8/')
    #PLOTS.set_star(-1071.46632, 534.761347)
    PLOTS.plot()
