#!/usr/bin/env python2

""" Data object to store decay channel characteristic values. """

from ROOT import kGreen, kCyan, kBlue, kMagenta
from ROOT import kPink, kViolet, kAzure, kTeal
from Logger import LGR

class DecayChannel(object):

    """ Data object to store decay channel characteristic values. """

    def __init__(self):

        """ Initialize object variables. """

        self._susy = []
        self._sm = []
        self._br = []

    def fill_dcs(self, decay):

        """ Fill object variables. """

        self._classify_particles(decay[1])
        self._br.append(decay[0])

    def _classify_particles(self, id_particles):

        """ Classifies the list id_particles into a category. A category is a
        combination from a SUSY and an SM subcategory. The SUSY subcategory
        consists of:
            gluino, n1, n2, c1
        The SM subcategory consists of:
            qq, tt, qt, ll, g, y, W, Z """

        # Rely on the fact that the first particle is always a SUSY particle,
        # while the remaining particles are all SM particles (RPC SUSY!)
        self._susy.append(self._classify_particles_susy(abs(id_particles[0])))
        self._sm.append(self._classify_particles_sm([abs(a) for a in
                                                     id_particles[1:]]))

    def _classify_particles_susy(self, id_particle):

        """ Classify integer id_particle into SUSY subcategory (see
        self._classify_particles()) for details. """

        if id_particle == 1000021:
            return 1
        elif id_particle == 1000022:
            return 2
        elif id_particle == 1000023:
            return 3
        elif id_particle == 1000024:
            return 4
        else:
            LGR.warning('Decay channel category for SUSY particle %s not '
                        'found.'.format(id_particle))
            return 9

    def _classify_particles_sm(self, id_particles):

        """ Classify list id_particles into SM subcategory (see
        self._classify_particles() for details. """

        cat_sm = 9
        if len(id_particles) == 1:
            if id_particles[0] == 21:
                # g
                cat_sm = 5
            elif id_particles[0] == 22:
                # y
                cat_sm = 6
            elif id_particles[0] == 23:
                # Z
                cat_sm = 8
            elif id_particles[0] == 24:
                # W
                cat_sm = 7
        elif len(id_particles) == 2:
            if id_particles[0] in [1, 2, 3, 4, 5]:
                if id_particles[1] in [1, 2, 3, 4, 5]:
                    # qq
                    cat_sm = 1
                elif id_particles[1] in [6]:
                    # qt
                    cat_sm = 3
            elif id_particles[0] in [6]:
                if id_particles[1] in [1, 2, 3, 4, 5]:
                    # qt
                    cat_sm = 3
                elif id_particles[1] in [6]:
                    # tt
                    cat_sm = 2
            elif id_particles[0] in [11, 12, 13, 14, 15, 16]:
                if id_particles[1] in [11, 12, 13, 14, 15, 16]:
                    # ll
                    cat_sm = 4

        if cat_sm == 9:
            LGR.warning('Decay channel category for SM particles %s not '
                        'found.'.format(id_particles))

        return cat_sm

    def get_susy(self):

        """ Get SUSY particles list. """

        return self._susy

    def get_susy_ps(self):

        """ Get number of different distinguished SUSY processes. """

        return 4

    def get_sm(self):

        """ Get SM particles list. """

        return self._sm

    def get_sm_ps(self):

        """ Get number of differente distinguished SM processes. """

        return 8

    def get_br(self):

        """ Get branching ratios list. """

        return self._br

    def get_ps(self, ps_susy, ps_sm):

        """ Return title for category combination. """

        return '{}{}'.format(self._get_ps_susy(ps_susy),
                             self._get_ps_sm(ps_sm))

    def _get_ps_susy(self, ps_susy):

        """ Return title for SUSY process. """

        if ps_susy == 1:
            return '#tilde{g} '
        if ps_susy == 2:
            return '#tilde{#chi}_{1}^{0}'
        if ps_susy == 3:
            return '#tilde{#chi}_{2}^{0}'
        if ps_susy == 4:
            return '#tilde{#chi}_{1}^{#pm}'
        return '?'

    def _get_ps_sm(self, ps_sm):

        """ Return title for SM process. """

        if ps_sm == 1:
            return 'q#bar{q}'
        if ps_sm == 2:
            return 't#bar{t}'
        if ps_sm == 3:
            return 'qt'
        if ps_sm == 4:
            return 'l#bar{l}'
        if ps_sm == 5:
            return 'g'
        if ps_sm == 6:
            return '#gamma'
        if ps_sm == 7:
            return 'W'
        if ps_sm == 8:
            return 'Z'
        return '?'

    def get_color(self, ps_susy, ps_sm):

        """ Return color for category combination. """

        if ps_susy == 1:
            if ps_sm == 1:
                return kPink+2
            if ps_sm == 2:
                return kPink+5
            if ps_sm == 3:
                return kPink+7
            if ps_sm == 4:
                return kMagenta
            if ps_sm == 5:
                return kMagenta+1
            if ps_sm == 6:
                return kMagenta+2
            if ps_sm == 7:
                return kMagenta+3
            if ps_sm == 8:
                return kMagenta-1
        if ps_susy == 2:
            if ps_sm == 1:
                return kViolet+2
            if ps_sm == 2:
                return kViolet+5
            if ps_sm == 3:
                return kViolet+7
            if ps_sm == 4:
                return kBlue
            if ps_sm == 5:
                return kBlue+1
            if ps_sm == 6:
                return kBlue+2
            if ps_sm == 7:
                return kBlue+3
            if ps_sm == 8:
                return kBlue-1
        if ps_susy == 3:
            if ps_sm == 1:
                return kAzure+2
            if ps_sm == 2:
                return kAzure+5
            if ps_sm == 3:
                return kAzure+7
            if ps_sm == 4:
                return kCyan
            if ps_sm == 5:
                return kCyan+1
            if ps_sm == 6:
                return kCyan+2
            if ps_sm == 7:
                return kCyan+3
            if ps_sm == 8:
                return kCyan-1
        if ps_susy == 4:
            if ps_sm == 1:
                return kTeal+2
            if ps_sm == 2:
                return kTeal+5
            if ps_sm == 3:
                return kTeal+7
            if ps_sm == 4:
                return kGreen
            if ps_sm == 5:
                return kGreen+1
            if ps_sm == 6:
                return kGreen+2
            if ps_sm == 7:
                return kGreen+3
            if ps_sm == 8:
                return kGreen-1

        # If all fails...
        return kBlack
