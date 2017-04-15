#!/usr/bin/env python2

""" Mass scan. """

from MassScan import MassScan

if __name__ == "__main__":
    X = [20*i for i in range(5, 13)]
    Y = [100*i for i in range(3, 13)]

    MY_SCAN = MassScan()
    MY_SCAN.set_threshold(.001)
    MY_SCAN.l_prmtr_x = X
    MY_SCAN.l_prmtr_y = Y
    MY_SCAN.set_parameter_add_scale_y(2, 2.)

    MY_SCAN.set_parameter(23, 1)

    output = 'output80_higgsino'
    name = 'final-try13'

    PLOTS = MY_SCAN.do_scan()
    PLOTS.set_rootfile('{}/{}.root'.format(output, name))
    PLOTS.set_directory('{}/{}'.format(output, name))
    #PLOTS.set_star(-1071.46632, 534.761347)
    PLOTS.plot()
