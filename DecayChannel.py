#!/usr/bin/env python2

""" Data object to store decay channel characteristic values. """

from ROOT import kGreen, kCyan, kBlue, kMagenta, kPink, kViolet
from ROOT import kAzure, kTeal, kOrange, kRed, kYellow, kSpring, kGray
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
        elif id_particle == 1000025:
            return 5
        elif id_particle in [1000001, 1000002, 1000003, 1000004,
                             2000001, 2000002, 2000003, 2000004]:
            return 6
        elif id_particle in [1000005, 1000006, 2000005, 2000006]:
            return 7
        elif id_particle in [1000011, 1000012, 1000013, 1000014,
                             1000015, 1000016, 2000011, 2000012,
                             2000013, 2000014, 2000015, 2000016]:
            return 8
        elif id_particle == 1000037:
            return 9
        elif id_particle == 1000035:
            return 10
        else:
            LGR.warning('Decay channel category for SUSY particle %s not '
                        'found.', id_particle)
            return 0

    def _classify_particles_sm(self, id_particles):

        """ Classify list id_particles into SM subcategory (see
        self._classify_particles() for details. """

        # 0 means undefined
        cat_sm = 0
        if len(id_particles) == 1:
            if id_particles[0] == 21:
                # g
                cat_sm = 7
            elif id_particles[0] == 22:
                # y
                cat_sm = 8
            elif id_particles[0] == 23:
                # Z
                cat_sm = 10
            elif id_particles[0] == 24:
                # W
                cat_sm = 9
            elif id_particles[0] == 25:
                # h
                cat_sm = 11
            elif id_particles[0] in [1, 2, 3, 4, 5]:
                # q
                cat_sm = 12
            elif id_particles[0] == 6:
                # t
                cat_sm = 13
            elif id_particles[0] in [11, 12, 13, 14, 15, 16]:
                # l
                cat_sm = 14
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
            elif id_particles[0] in [11, 13, 15]:
                if id_particles[1] in [11, 13, 15]:
                    # ll
                    cat_sm = 4
                elif id_particles[1] in [12, 14, 16]:
                    # nu l
                    cat_sm = 5
            elif id_particles[0] in [12, 14, 16]:
                if id_particles[1] in [11, 13, 15]:
                    # nu l
                    cat_sm = 5
                elif id_particles[1] in [12, 14, 16]:
                    # nu nu
                    cat_sm = 6

        if cat_sm == 0:
            LGR.warning('Decay channel category for SM particle(s) %s not '
                        'found.', id_particles)

        return cat_sm

    def get_susy(self):

        """ Get SUSY particles list. """

        return self._susy

    def get_susy_ps(self):

        """ Get number of different distinguished SUSY processes. """

        return 10

    def get_sm(self):

        """ Get SM particles list. """

        return self._sm

    def get_sm_ps(self):

        """ Get number of differente distinguished SM processes. """

        return 14

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
        if ps_susy == 5:
            return '#tilde{#chi}_{3}^{0}'
        if ps_susy == 6:
            return '#tilde{q}_{12}'
        if ps_susy == 7:
            return '#tilde{q}_{3}'
        if ps_susy == 8:
            return '#tilde{l}'
        if ps_susy == 9:
            return '#tilde{#chi}_{2}^{#pm}'
        if ps_susy == 10:
            return '#tilde{#chi}_{4}^{0}'
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
            return 'l#nu'
        if ps_sm == 6:
            return '#nu#nu'
        if ps_sm == 7:
            return 'g'
        if ps_sm == 8:
            return '#gamma'
        if ps_sm == 9:
            return 'W'
        if ps_sm == 10:
            return 'Z'
        if ps_sm == 11:
            return 'h'
        if ps_sm == 12:
            return 'q'
        if ps_sm == 13:
            return 't'
        if ps_sm == 14:
            return 'l'
        return '?'

    def get_color(self, ps_susy, ps_sm):

        """ Return color for category combination. """

        if ps_susy == 1:
            if ps_sm in [1, 12]:
                return kPink+2
            if ps_sm in [2, 13]:
                return kPink+5
            if ps_sm == 3:
                return kPink+7
            if ps_sm in [4, 5, 14]:
                return kMagenta
            if ps_sm in [6, 7]:
                return kMagenta+1
            if ps_sm == 8:
                return kMagenta+2
            if ps_sm == 9:
                return kMagenta+3
            if ps_sm == 10:
                return kMagenta-1
            if ps_sm == 11:
                return kMagenta+4
        if ps_susy in [2, 6]:
            if ps_sm in [1, 12]:
                return kViolet+2
            if ps_sm in [2, 13]:
                return kViolet+5
            if ps_sm == 3:
                return kViolet+7
            if ps_sm in [4, 5, 14]:
                return kBlue
            if ps_sm in [6, 7]:
                return kBlue+1
            if ps_sm == 8:
                return kBlue+2
            if ps_sm == 9:
                return kBlue+3
            if ps_sm == 10:
                return kBlue-1
            if ps_sm == 11:
                return kBlue+4
        if ps_susy in [3, 7]:
            if ps_sm in [1, 12]:
                return kAzure+2
            if ps_sm in [2, 13]:
                return kAzure+5
            if ps_sm == 3:
                return kAzure+7
            if ps_sm in [4, 5, 14]:
                return kCyan
            if ps_sm in [6, 7]:
                return kCyan+1
            if ps_sm == 8:
                return kCyan+2
            if ps_sm == 9:
                return kCyan+3
            if ps_sm == 10:
                return kCyan-1
            if ps_sm == 11:
                return kCyan+4
        if ps_susy in [4, 8]:
            if ps_sm in [1, 12]:
                return kTeal+2
            if ps_sm in [2, 13]:
                return kTeal+5
            if ps_sm == 3:
                return kTeal+7
            if ps_sm in [4, 5, 14]:
                return kGreen
            if ps_sm in [6, 7]:
                return kGreen+1
            if ps_sm == 8:
                return kGreen+2
            if ps_sm == 9:
                return kGreen+3
            if ps_sm == 10:
                return kGreen-1
            if ps_sm == 11:
                return kGreen+4
        if ps_susy in [5, 10]:
            if ps_sm in [1, 12]:
                return kOrange+2
            if ps_sm in [2, 13]:
                return kOrange+5
            if ps_sm == 3:
                return kOrange+7
            if ps_sm in [4, 5, 14]:
                return kRed
            if ps_sm in [6, 7]:
                return kRed+1
            if ps_sm == 8:
                return kRed+2
            if ps_sm == 9:
                return kRed+3
            if ps_sm == 10:
                return kRed-1
            if ps_sm == 11:
                return kRed+4
        if ps_susy in [9]:
            if ps_sm in [1, 12]:
                return kSpring+2
            if ps_sm in [2, 13]:
                return kSpring+5
            if ps_sm == 3:
                return kSpring+7
            if ps_sm in [4, 5, 14]:
                return kYellow
            if ps_sm in [6, 7]:
                return kYellow+1
            if ps_sm == 8:
                return kYellow+2
            if ps_sm == 9:
                return kYellow+3
            if ps_sm == 10:
                return kYellow-1
            if ps_sm == 11:
                return kYellow+4

        # If all fails...
        return kGray
