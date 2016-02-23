#!/usr/bin/env python2

""" Mass scan. """

from MassScan import MassScan

if __name__ == "__main__":
    X = [100*i for i in range(1, 10)]
    Y = [100*i for i in range(1, 10)]
    for grid in range(1, 13):
        for limit in ['a', 'b']:

            MY_SCAN = MassScan()
            MY_SCAN.set_threshold(.01)
            MY_SCAN.l_prmtr_x = X
            MY_SCAN.l_prmtr_y = Y

            output = 'output16'
            name = 'grid{}{}'.format(grid, limit)

            if grid % 2 == 1:
                if limit == 'a':
                    shift = 10
                else:
                    shift = 30
            else:
                if limit == 'a':
                    shift = 20
                else:
                    shift = 100

            if grid == 1:
                MY_SCAN.set_parameter(3, 1)
                MY_SCAN.set_parameter_add_y(2, shift)
            elif grid == 2:
                MY_SCAN.set_parameter(3, 23)
                MY_SCAN.set_parameter_add_y(1, shift)
            elif grid == 3:
                MY_SCAN.set_parameter(3, 1)
                MY_SCAN.set_parameter_add_x(414243, 0)
                MY_SCAN.set_parameter_add_x(444546474849, 0)
                MY_SCAN.set_parameter_add_y(2, shift)
            elif grid == 4:
                MY_SCAN.set_parameter(3, 23)
                MY_SCAN.set_parameter_add_x(414243, 0)
                MY_SCAN.set_parameter_add_x(444546474849, 0)
                MY_SCAN.set_parameter_add_y(1, shift)
            elif grid == 5:
                MY_SCAN.set_parameter(3, 1)
                MY_SCAN.set_parameter_add_x(414243, 0)
                MY_SCAN.set_parameter_add_y(2, shift)
            elif grid == 6:
                MY_SCAN.set_parameter(3, 23)
                MY_SCAN.set_parameter_add_x(414243, 0)
                MY_SCAN.set_parameter_add_y(1, shift)
            elif grid == 7:
                MY_SCAN.set_parameter(3, 1)
                MY_SCAN.set_parameter_add_x(444546474849, 0)
                MY_SCAN.set_parameter_add_y(2, shift)
            elif grid == 8:
                MY_SCAN.set_parameter(3, 23)
                MY_SCAN.set_parameter_add_x(444546474849, 0)
                MY_SCAN.set_parameter_add_y(1, shift)
            elif grid == 9:
                MY_SCAN.set_parameter(414243, 1)
                MY_SCAN.set_parameter_add_y(2, shift)
            elif grid == 10:
                MY_SCAN.set_parameter(414243, 23)
                MY_SCAN.set_parameter_add_y(1, shift)
            elif grid == 11:
                MY_SCAN.set_parameter(44454748, 1)
                MY_SCAN.set_parameter_add_y(2, shift)
            elif grid == 12:
                MY_SCAN.set_parameter(44454748, 23)
                MY_SCAN.set_parameter_add_y(1, shift)

            PLOTS = MY_SCAN.do_scan()
            PLOTS.set_rootfile('{}/{}.root'.format(output, name))
            PLOTS.set_directory('{}/{}'.format(output, name))
            #PLOTS.set_star(-1071.46632, 534.761347)
            PLOTS.plot()
