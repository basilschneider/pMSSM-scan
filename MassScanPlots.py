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

        # Branching ratios
        for no_leptons in range(len(self.br_leptons)):
            name = 'br_{}_leptons'.format(no_leptons)
            title = 'branching ratio into {} leptons'.format(no_leptons)
            self._make_plot(name, title, self.br_leptons[no_leptons], True)

        for no_jets in range(len(self.br_jets)):
            name = 'br_{}_jets'.format(no_jets)
            title = 'branching ratio into {} jets'.format(no_jets)
            self._make_plot(name, title, self.br_jets[no_jets], True)

        # Cross-sections
        name = 'xs_total'
        title = 'total XS [pb]'
        self._make_plot(name, title, self.xs_total)

        name = 'xs_gluino_gluino'
        title = 'XS(pp #rightarrow #tilde{g}#tilde{g}) [pb]'
        self._make_plot(name, title, self.xs_gluinos)

        # Masses
        name = 'm_gluino'
        title = 'm_{#tilde{g}} [GeV]'
        self._make_plot(name, title, self.m_gluino)

        name = 'm_neutralino1'
        title = 'm_{#chi_{1}^{0}} [GeV]'
        self._make_plot(name, title, self.m_neutralino1)

        name = 'm_neutralino2'
        title = 'm_{#chi_{2}^{0}} [GeV]'
        self._make_plot(name, title, self.m_neutralino2)

        name = 'm_chargino1'
        title = 'm_{#chi_{1}^{#pm}} [GeV]'
        self._make_plot(name, title, self.m_chargino1)

        name = 'm_smhiggs'
        title = 'm_{h^{0}} [GeV]'
        self._make_plot(name, title, self.m_smhiggs)

        # Mass differences
        name = 'm_gluino-m_chargino1'
        title = 'm_{#tilde{g}} - m_{#chi_{1}^{#pm}} [GeV]'
        self._make_plot(name, title, self.m_diff_g_c1)

        name = 'm_chargino1-m_neutralino1'
        title = 'm_{#chi_{1}^{#pm}} - m_{#chi_{1}^{0}} [GeV]'
        self._make_plot(name, title, self.m_diff_c1_n1)

        # Close root file
        if self._toolbox.rootfile.IsOpen():
            self._toolbox.rootfile.Close()

    def _make_plot(self, name, title, coordinate_z, percentage=False):

        """ Create specific plot. """

        # Axes are predefined for now
        axis_x = 'M_{3} [GeV]'
        axis_y = '#mu [GeV]'

        # Set z range
        z_low = 0.
        if percentage:
            z_high = 100.
        else:
            z_high = max(coordinate_z)+1.

        # Set scaling constant
        if percentage:
            scale = 100.
        else:
            scale = 1.

        # Define TH2
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y)
        self._toolbox.modify_axes(axis_x, axis_y, z_low, z_high)

        # Fill numbers
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   coordinate_z, scale)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

    def set_rootfile(self, s_rootfile_name):

        """ Set rootfile name in toolbox. """

        self._toolbox.rootfile = TFile(s_rootfile_name, 'UPDATE')

    def set_directory(self, s_directory):

        """ Set directory in which objects are stored. """

        self._toolbox.directory = s_directory

    def set_star(self, coordinate_x, coordinate_y):

        """ Set star to be plotted at coordinates (x/y). """

        self._star = [coordinate_x, coordinate_y]
