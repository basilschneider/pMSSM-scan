#!/usr/bin/env python2

""" Plotting class for mass scan. """

from os import system
from ROOT import TFile, gStyle  # pylint: disable=import-error
from Logger import LGR
from ToolboxTH2 import ToolboxTH2
from ToolboxHelper import safe_divide


class MassScanPlots(object):

    """ Plotting class for mass scan. """

    def __init__(self):

        """ Initialize object variables. """

        # X/Y coordinates for plotting
        self.coordinate_x = []
        self.coordinate_y = []

        # Axes labels
        self._axis_x = 'M_{3} [GeV]'
        self._axis_y = '#mu [GeV]'

        # Branching ratios
        self.br_leptons = [[], [], [], [], []]
        self.br_jets = [[], [], [], [], [], [], [], [], [], [], [], [], []]
        self.br_photons = [[], [], [], []]
        self.br_met = [[], [], [], [], []]

        # xs's
        self.xs13_incl = []
        self.xs13_strong = []
        self.xs13_gluinos = []
        self.xs8_incl = []
        self.xs8_strong = []

        # Dominant production particle id
        self.dom_id1 = []
        self.dom_id2 = []

        # Masses
        self.m_gluino = []
        self.m_neutralino1 = []
        self.m_neutralino2 = []
        self.m_neutralino3 = []
        self.m_chargino1 = []
        self.m_stop1 = []
        self.m_stop2 = []
        self.m_smhiggs = []
        self.m_sdown_l = []
        self.m_sdown_r = []
        self.m_sup_l = []
        self.m_sup_r = []
        self.m_sstrange_l = []
        self.m_sstrange_r = []
        self.m_scharm_l = []
        self.m_scharm_r = []

        # Lifetimes
        self.ct_gluino = []
        self.ct_chargino1 = []
        self.ct_neutralino2 = []

        # Decay channels
        self.dc_gluino = []
        self.dc_chargino1 = []
        self.dc_chargino2 = []
        self.dc_neutralino2 = []
        self.dc_neutralino3 = []
        self.dc_sdown_l = []
        self.dc_sdown_r = []
        self.dc_sup_l = []
        self.dc_sup_r = []
        self.dc_sstrange_l = []
        self.dc_sstrange_r = []
        self.dc_scharm_l = []
        self.dc_scharm_r = []

        # Signal strength
        self.mu = []  # pylint: disable=invalid-name

        # Star to be plotted on all TH2's
        self._star = [0, 0]

        self._toolbox = ToolboxTH2()

    def plot(self):

        """ ROOT plotting. """

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

        name = 'm_neutralino3'
        title = 'm_{#chi_{3}^{0}} [GeV]'
        self._make_plot(name, title, self.m_neutralino3)

        name = 'm_chargino1'
        title = 'm_{#chi_{1}^{#pm}} [GeV]'
        self._make_plot(name, title, self.m_chargino1)

        name = 'm_stop1'
        title = 'm_{#tilde{t_{1}}} [GeV]'
        self._make_plot(name, title, self.m_stop1)

        name = 'm_stop2'
        title = 'm_{#tilde{t_{2}}} [GeV]'
        self._make_plot(name, title, self.m_stop2)

        name = 'm_smhiggs'
        title = 'm_{h^{0}} [GeV]'
        self._make_plot(name, title, self.m_smhiggs)

        name = 'm_sdown_l'
        title = 'm_{#tilde{d}_{L}} [GeV]'
        self._make_plot(name, title, self.m_sdown_l)

        name = 'm_sdown_r'
        title = 'm_{#tilde{d}_{R}} [GeV]'
        self._make_plot(name, title, self.m_sdown_r)

        name = 'm_sup_l'
        title = 'm_{#tilde{u}_{L}} [GeV]'
        self._make_plot(name, title, self.m_sup_l)

        name = 'm_sup_r'
        title = 'm_{#tilde{u}_{R}} [GeV]'
        self._make_plot(name, title, self.m_sup_r)

        name = 'm_sstrange_l'
        title = 'm_{#tilde{s}_{L}} [GeV]'
        self._make_plot(name, title, self.m_sstrange_l)

        name = 'm_sstrange_r'
        title = 'm_{#tilde{s}_{R}} [GeV]'
        self._make_plot(name, title, self.m_sstrange_r)

        name = 'm_scharm_l'
        title = 'm_{#tilde{c}_{L}} [GeV]'
        self._make_plot(name, title, self.m_scharm_l)

        name = 'm_scharm_r'
        title = 'm_{#tilde{c}_{R}} [GeV]'
        self._make_plot(name, title, self.m_scharm_r)

        # Lifetimes
        gStyle.SetPaintTextFormat('3.2g')

        name = 'ct_gluino'
        title = 'c#tau_{#tilde{g}} [mm]'
        self._make_plot(name, title, self.ct_gluino, decimals=99)

        name = 'ct_chargino1'
        title = 'c#tau_{#tilde{#chi}_{1}^{#pm}} [mm]'
        self._make_plot(name, title, self.ct_chargino1, decimals=99)

        name = 'ct_neutralino2'
        title = 'c#tau_{#tilde{#chi}_{2}^{0}} [mm]'
        self._make_plot(name, title, self.ct_neutralino2, decimals=99)

        gStyle.SetPaintTextFormat('g')

        # Mass differences
        name = 'm_gluino-m_chargino1'
        title = 'm_{#tilde{g}} - m_{#chi_{1}^{#pm}} [GeV]'
        self._make_plot(name, title, [a-b for a, b in
                                      zip(self.m_gluino, self.m_chargino1)])

        name = 'm_chargino1-m_neutralino1'
        title = 'm_{#chi_{1}^{#pm}} - m_{#chi_{1}^{0}} [GeV]'
        self._make_plot(name, title, [a-b for a, b in
                                      zip(self.m_chargino1,
                                          self.m_neutralino1)])

        name = 'm_neutralino3-m_neutralino1'
        title = 'm_{#chi_{3}^{0}} - m_{#chi_{1}^{0}} [GeV]'
        self._make_plot(name, title, [a-b for a, b in
                                      zip(self.m_neutralino3,
                                          self.m_neutralino1)])

        name = 'm_neutralino3-m_chargino1'
        title = 'm_{#chi_{3}^{0}} - m_{#chi_{1}^{#pm}} [GeV]'
        self._make_plot(name, title, [a-b for a, b in
                                      zip(self.m_neutralino3,
                                          self.m_chargino1)])

        # Cross-sections
        name = 'xs13_incl'
        title = '#sigma_{inclusive} (13 TeV) [fb]'
        self._make_plot(name, title, self.xs13_incl)

        name = 'xs13_strong'
        title = '#sigma_{strong}/#sigma_{inclusive} (13 TeV)'
        self._make_plot(name, title, self.xs13_strong, True)

        name = 'xs13_gluino_gluino'
        title = '#sigma (pp #rightarrow #tilde{g}#tilde{g})/' \
                '#sigma_{inclusive} (13 TeV)'
        self._make_plot(name, title, self.xs13_gluinos, True)

        name = 'xs8_incl'
        title = '#sigma_{inclusive} (8 TeV) [fb]'
        self._make_plot(name, title, self.xs8_incl)

        name = 'xs8_strong'
        title = '#sigma_{strong}/#sigma_{inclusive} (8 TeV)'
        self._make_plot(name, title, self.xs8_strong, True)

        name = 'xs13_xs8'
        title = '#sigma_{incl} (13 TeV)/#sigma_{incl} (8 TeV)'
        self._make_plot(name, title, [safe_divide(a, b) for a, b in
                                      zip(self.xs13_incl, self.xs8_incl)])

        # Dominant cross section particles
        gStyle.SetPaintTextFormat('7.0f')

        name = 'dom1'
        title = 'Dominant cross section particle 1'
        self._make_plot(name, title, self.dom_id1)

        name = 'dom2'
        title = 'Dominant cross section particle 2'
        self._make_plot(name, title, self.dom_id2)

        gStyle.SetPaintTextFormat('g')

        # Decay channels
        name = 'dc_gluino'
        title = 'Relative decay channels of #tilde{g}'
        self._make_plot_dc(name, title, self.dc_gluino)

        name = 'dc_chargino1'
        title = 'Relative decay channels of #tilde{#chi}_{1}^{#pm}'
        self._make_plot_dc(name, title, self.dc_chargino1)

        name = 'dc_chargino2'
        title = 'Relative decay channels of #tilde{#chi}_{2}^{#pm}'
        self._make_plot_dc(name, title, self.dc_chargino2)

        name = 'dc_neutralino2'
        title = 'Relative decay channels of #tilde{#chi}_{2}^{0}'
        self._make_plot_dc(name, title, self.dc_neutralino2)

        name = 'dc_neutralino3'
        title = 'Relative decay channels of #tilde{#chi}_{3}^{0}'
        self._make_plot_dc(name, title, self.dc_neutralino3)

        name = 'dc_sdown_l'
        title = 'Relative decay channels of #tilde{d}_{L}'
        self._make_plot_dc(name, title, self.dc_sdown_l)

        name = 'dc_sdown_r'
        title = 'Relative decay channels of #tilde{d}_{R}'
        self._make_plot_dc(name, title, self.dc_sdown_r)

        name = 'dc_sup_l'
        title = 'Relative decay channels of #tilde{u}_{L}'
        self._make_plot_dc(name, title, self.dc_sup_l)

        name = 'dc_sup_r'
        title = 'Relative decay channels of #tilde{u}_{R}'
        self._make_plot_dc(name, title, self.dc_sup_r)

        name = 'dc_sstrange_l'
        title = 'Relative decay channels of #tilde{s}_{L}'
        self._make_plot_dc(name, title, self.dc_sstrange_l)

        name = 'dc_sstrange_r'
        title = 'Relative decay channels of #tilde{s}_{R}'
        self._make_plot_dc(name, title, self.dc_sstrange_r)

        name = 'dc_scharm_l'
        title = 'Relative decay channels of #tilde{c}_{L}'
        self._make_plot_dc(name, title, self.dc_scharm_l)

        name = 'dc_scharm_r'
        title = 'Relative decay channels of #tilde{c}_{R}'
        self._make_plot_dc(name, title, self.dc_scharm_r)

        # Branching ratios
        for no_leptons in range(len(self.br_leptons)):
            name = 'br_{}_leptons'.format(no_leptons)
            title = 'BR into {} leptons'.format(no_leptons)
            self._make_plot(name, title, self.br_leptons[no_leptons], True)

        for no_jets in range(len(self.br_jets)):
            name = 'br_{}_jets'.format(no_jets)
            title = 'BR into {} jets'.format(no_jets)
            self._make_plot(name, title, self.br_jets[no_jets], True)

        for no_photons in range(len(self.br_photons)):
            name = 'br_{}_photons'.format(no_photons)
            title = 'BR into {} photons'.format(no_photons)
            self._make_plot(name, title, self.br_photons[no_photons], True)

        # Cross-sections times branching ratio
        for no_leptons in range(len(self.br_leptons)):
            name = 'xs13_x_br_{}_leptons'.format(no_leptons)
            title = '#sigma #times BR(#tilde{{g}}#tilde{{g}} #rightarrow {} ' \
                    'leptons) [fb]'.format(no_leptons)
            self._make_plot(name, title,
                            [a*b for a, b in
                             zip(self.br_leptons[no_leptons], self.xs13_incl)])

        # Signal strength
        name = 'mu'
        title = '#mu'
        self._make_plot(name, title, self.mu, decimals=2)

        # Close root file
        if self._toolbox.rootfile.IsOpen():
            self._toolbox.rootfile.Close()

        # Move used SLHA template to output folder
        system('cp suspect2_lha.template {}'.format(self._toolbox.directory))
        system('mv susyhit_slha_*.out {}'.format(self._toolbox.directory))
        system('mv suspect2_*.out {}'.format(self._toolbox.directory))

        # Move SModelS output to output folder
        system('mv smodels_summary_*.txt {} 2>/dev/null'
               .format(self._toolbox.directory))

    def _make_plot(self, name, title, coordinate_z, percentage=False,
                   decimals=1):

        """ Create specific plot. """

        # If there's nothing to plot, don't plot it
        if len(coordinate_z) == 0:
            return

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
                                   coordinate_z, scale, decimals)
        self._toolbox.plot_star(self._star)
        self._toolbox.plot_diagonal()
        self._toolbox.save()

    def _make_plot_dc(self, name, title, dcs):

        """ Create plot showing relative decay channels. """

        # If there's nothing to plot, don't plot it
        if len(dcs) == 0:
            return

        # The TH2 needs to have ten times as many bins per axis
        self._toolbox.create_histogram(name, title, self.coordinate_x,
                                       self.coordinate_y, 10)
        self._toolbox.modify_axes(self._axis_x, self._axis_y)

        # Fill numbers
        self._toolbox.plot_dcs(self.coordinate_x, self.coordinate_y, dcs)
        self._toolbox.plot_diagonal()
        self._toolbox.save()

    def set_axis(self, axis_x, axis_y, axis_x_add, axis_y_add):

        """ Set axis labels. """

        # Set the main label
        axis_x = self._get_axis_label(axis_x)
        axis_y = self._get_axis_label(axis_y)

        # Add all additional labels from the dictionaries
        for key, value in axis_x_add.iteritems():
            if value == 0:
                axis_x += ' = {}'.format(self._get_axis_label(key))
            elif value > 0:
                axis_x += ' = {} - {}'.format(self._get_axis_label(key), value)
            else:
                axis_x += ' = {} + {}'.format(self._get_axis_label(key),
                                              abs(value))
        for key, value in axis_y_add.iteritems():
            if value == 0:
                axis_y += ' = {}'.format(self._get_axis_label(key))
            elif value > 0:
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
        if axis == 4142:
            return 'm_{q_{12L}}'
        if axis == 44454748:
            return 'm_{q_{12R}}'
        return str(axis)

    def set_rootfile(self, s_rootfile_name):

        """ Set rootfile name in toolbox. """

        # If rootfile is located in a subdirectory, create directory first
        if '/' in s_rootfile_name:
            system('mkdir -p {}'
                   .format('/'.join(s_rootfile_name.split('/')[:-1])))

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
