#!/usr/bin/env python2

""" Plotting class for mass scan. """

from os import system
from ROOT import TFile  # pylint: disable=import-error
from Logger import LGR
from ToolboxTH2 import ToolboxTH2


class MassScanPlots(object):

    """ Plotting class for mass scan. """

    # X/Y coordinates for plotting
    coordinate_x = []
    coordinate_y = []

    # Axes labels
    _axis_x = 'M_{3} [GeV]'
    _axis_y = '#mu [GeV]'

    # Branching ratios
    br_leptons = [[], [], [], [], []]
    br_jets = [[], [], [], [], [], [], [], [], [], [], [], [], []]
    br_photons = [[], [], [], []]
    br_met = [[], [], [], [], []]

    # xs's
    xs_incl = []
    xs_strong = []
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

    # Signal strength
    mu = []  # pylint: disable=invalid-name

    # Star to be plotted on all TH2's
    _star = [0, 0]

    _toolbox = ToolboxTH2()

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

        for no_photons in range(len(self.br_photons)):
            name = 'br_{}_photons'.format(no_photons)
            title = 'branching ratio into {} photons'.format(no_photons)
            self._make_plot(name, title, self.br_photons[no_photons], True)

        # Cross-sections
        name = 'xs_incl'
        title = '#sigma_{inclusive} [fb]'
        self._make_plot(name, title, self.xs_incl)

        name = 'xs_strong'
        title = '#sigma_{strong}/#sigma_{inclusive}'
        self._make_plot(name, title, self.xs_strong, True)

        name = 'xs_gluino_gluino'
        title = '#sigma (pp #rightarrow #tilde{g}#tilde{g})/#sigma_{inclusive}'
        self._make_plot(name, title, self.xs_gluinos, True)

        # Cross-sections times branching ratio
        for no_leptons in range(len(self.br_leptons)):
            name = 'xs_x_br_{}_leptons'.format(no_leptons)
            title = '#sigma #times BR into {} leptons [fb]'.format(no_leptons)
            self._make_plot(name, title,
                            [a*b for a, b in
                             zip(self.br_leptons[no_leptons], self.xs_incl)])

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

        # Signal strength
        name = 'mu'
        title = '#mu'
        self._make_plot(name, title, self.mu, True)

        # Close root file
        if self._toolbox.rootfile.IsOpen():
            self._toolbox.rootfile.Close()

        # Move used SLHA template to output folder
        system('cp suspect2_lha.template {}'.format(self._toolbox.directory))

        # Move SModelS output to output folder
        system('mv smodels_summary_*.txt {}'.format(self._toolbox.directory))

    def _make_plot(self, name, title, coordinate_z, percentage=False):

        """ Create specific plot. """

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
        self._toolbox.modify_axes(self._axis_x, self._axis_y, z_low, z_high)

        # Fill numbers
        self._toolbox.plot_numbers(self.coordinate_x, self.coordinate_y,
                                   coordinate_z, scale)
        self._toolbox.plot_star(self._star)
        self._toolbox.save()

    def set_axis(self, axis_x, axis_y, axis_x_add, axis_y_add):

        """ Set axis labels. """

        # Set the main label
        axis_x = self._get_axis_label(axis_x)
        axis_y = self._get_axis_label(axis_y)

        # Add all additional labels from the dictionaries
        for key, value in axis_x_add.iteritems():
            if value > 0:
                axis_x += ' = {} - {}'.format(self._get_axis_label(key), value)
            else:
                axis_x += ' = {} + {}'.format(self._get_axis_label(key),
                                              abs(value))
        for key, value in axis_y_add.iteritems():
            if value > 0:
                axis_y += ' = {} - {}'.format(self._get_axis_label(key), value)
            else:
                axis_y += ' = {} + {}'.format(self._get_axis_label(key),
                                              abs(value))

        # Add unit
        axis_x += ' [GeV]'
        axis_y += ' [GeV]'

        self.set_axis_x(axis_x)
        self.set_axis_y(axis_y)

        LGR.debug('Set x axis to %s', axis_x)
        LGR.debug('Set y axis to %s', axis_y)

    def set_axis_x(self, axis_x):

        """ Set x axis label. """

        self._axis_x = axis_x

    def set_axis_y(self, axis_y):

        """ Set y axis label. """

        self._axis_y = axis_y

    def _get_axis_label(self, axis):

        """ Translate particle ID into string for axis labels. """

        if axis == 1:
            return 'M_{1}'
        if axis == 2:
            return 'M_{2}'
        if axis == 3:
            return 'M_{3}'
        if axis == 23:
            return '#mu'
        if axis == 414243:
            return 'm_{q_{L}}'
        if axis == 444546474849:
            return 'm_{q_{R}}'
        return str(axis)

    def set_rootfile(self, s_rootfile_name):

        """ Set rootfile name in toolbox. """

        self._toolbox.rootfile = TFile(s_rootfile_name, 'UPDATE')

    def get_directory(self):

        """ Get directory in which objects are stored. """

        return self._toolbox.directory

    def set_directory(self, s_directory):

        """ Set directory in which objects are stored. """

        self._toolbox.directory = s_directory

    def set_star(self, coordinate_x, coordinate_y):

        """ Set star to be plotted at coordinates (x/y). """

        self._star = [coordinate_x, coordinate_y]
