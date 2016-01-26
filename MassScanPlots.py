#!/usr/bin/env python2

""" Plotting class for mass scan. """

from Toolbox import ToolboxH2
from ROOT import TFile  # pylint: disable=import-error


class MassScanPlots(object):

    """ Plotting class for mass scan. """

    # X/Y coordinates for plotting
    coordinate_x = []
    coordinate_y = []

    # Branching ratios
    br_leptons = [[], [], [], [], []]
    br_jets = [[], [], [], [], [], [], [], [], [], [], [], [], []]
    br_met = [[], [], [], [], []]

    # xs's
    xs_total = []
    xs_gluinos = []

    # Masses
    m_gluino = []
    m_neutralino1 = []
    m_neutralino2 = []
    m_chargino1 = []
    m_smhiggs = []

    # Mass differences
    m_diff_g_c1 = []
    m_diff_c1_n1 = []

    # Star to be plotted on all TH2's
    _star = [0, 0]

    _toolbox = ToolboxH2()

    def plot(self):

        """ Root plotting """

        axis_x = 'M_{3} [GeV]'
        axis_y = '#mu [GeV]'

        # Branching ratios into leptons
        for no_leptons in range(len(self.br_leptons)):
            # Define TH2
            name = 'br_{}_leptons'.format(no_leptons)
            title = 'branching ratio into {} leptons'.format(no_leptons)
            self._toolbox.create_histogram(name, title, self.coordinate_x,
                                           self.coordinate_y)
            self._toolbox.modify_axes(axis_x, axis_y)

            # Fill numbers
            self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                       self.br_leptons[no_leptons], 100.)
            self._toolbox.plot_star(self._star)
            self._toolbox.save()

        # Branching ratios into jets
        for no_jets in range(len(self.br_jets)):
            # Define TH2
            name = 'br_{}_jets'.format(no_jets)
            title = 'branching ratio into {} jets'.format(no_jets)
            self._toolbox.create_histogram(name, title, self.coordinate_x,
                                           self.coordinate_y)
            self._toolbox.modify_axes(axis_x, axis_y)

            # Fill numbers
            self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                       self.br_jets[no_jets], 100.)
            self._toolbox.plot_star(self._star)
            self._toolbox.save()

        # total XS
        name = 'xs_total'
        title = 'total XS [pb]'
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y)
        self._toolbox.modify_axes(axis_x, axis_y, 0., max(self.xs_total)+1.)
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   self.xs_total)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

        # gluino-gluino XS
        name = 'xs_gluino_gluino'
        title = 'XS(pp #rightarrow #tilde{g}#tilde{g}) [pb]'
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y)
        self._toolbox.modify_axes(axis_x, axis_y, 0., max(self.xs_gluinos)+1.)
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   self.xs_gluinos)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

        # Gluino mass
        name = 'm_gluino'
        title = 'm_{#tilde{g}} [GeV]'
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y)
        self._toolbox.modify_axes(axis_x, axis_y, 0., max(self.m_gluino)+1.)
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   self.m_gluino)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

        # Neutralino 1 mass
        name = 'm_neutralino1'
        title = 'm_{#chi_{1}^{0}} [GeV]'
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y)
        self._toolbox.modify_axes(axis_x, axis_y, 0.,
                                  max(self.m_neutralino1)+1.)
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   self.m_neutralino1)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

        # Neutralino 2 mass
        name = 'm_neutralino2'
        title = 'm_{#chi_{2}^{0}} [GeV]'
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y)
        self._toolbox.modify_axes(axis_x, axis_y, 0.,
                                  max(self.m_neutralino2)+1.)
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   self.m_neutralino2)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

        # Chargino 1 mass
        name = 'm_chargino1'
        title = 'm_{#chi_{1}^{#pm}} [GeV]'
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y)
        self._toolbox.modify_axes(axis_x, axis_y, 0., max(self.m_chargino1)+1.)
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   self.m_chargino1)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

        # SM Higgs mass
        name = 'm_smhiggs'
        title = 'm_{h^{0}} [GeV]'
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y)
        self._toolbox.modify_axes(axis_x, axis_y, 0., max(self.m_smhiggs)+1.)
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   self.m_smhiggs)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

        # Mass difference gluino - chargino 1
        name = 'm_gluino-m_chargino1'
        title = 'm_{#tilde{g}} - m_{#chi_{1}^{#pm}} [GeV]'
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y)
        self._toolbox.modify_axes(axis_x, axis_y, 0., max(self.m_diff_g_c1)+1.)
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   self.m_diff_g_c1)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

        # Mass difference gluino - chargino 1
        name = 'm_chargino1-m_neutralino1'
        title = 'm_{#chi_{1}^{#pm}} - m_{#chi_{1}^{0}} [GeV]'
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y)
        self._toolbox.modify_axes(axis_x, axis_y, 0., max(self.m_diff_c1_n1)+1.)
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   self.m_diff_c1_n1)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

        # Close root file
        if self._toolbox.rootfile.IsOpen():
            self._toolbox.rootfile.Close()

    def set_rootfile(self, s_rootfile_name):

        """ Set rootfile name in toolbox. """

        self._toolbox.rootfile = TFile(s_rootfile_name, 'UPDATE')

    def set_directory(self, s_directory):

        """ Set directory in which objects are stored. """

        self._toolbox.directory = s_directory

    def set_star(self, coordinate_x, coordinate_y):

        """ Set star to be plotted at coordinates (x/y). """

        self._star = [coordinate_x, coordinate_y]
