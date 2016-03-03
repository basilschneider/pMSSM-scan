#!/usr/bin/env python2

""" Data object to store cross section characteric values. """

from re import search
from Logger import LGR
from PdgParticle import PdgParticle

class CrossSection(PdgParticle):

    """ Data object to store cross section characteristic values. """

    def __init__(self):

        """ Initialize object variables. """

        self._p1 = []
        self._p2 = []
        self._xs = []

    def get_xs(self, com, path):

        """ Get cross section from SLHA. """

        # Regex to be searched in SLHA file
        if com == 13:
            regex_xs = r'XSECTION *1\.30E\+04 *2212 2212 2'
        elif com == 8:
            regex_xs = r'XSECTION *8\.00E\+03 *2212 2212 2'
        else:
            raise ValueError('Only cross-sections of 8 or 13 TeV are allowed.')

        with open('{}/susyhit_slha.out'.format(path), 'r') as f_susyhit:
            found_xsec = False
            for line in f_susyhit:
                if found_xsec:
                    # Multiply by 1000. to get cross section in fb
                    self._xs.append(1000.*float(line.split()[6]))
                    found_xsec = False
                # If the xs matches, set bool, next line will have the xs
                if search(regex_xs, line):
                    LGR.debug(line.rstrip())
                    self._p1.append(int(line.split()[5]))
                    self._p2.append(int(line.split()[6]))
                    found_xsec = True

    def get_xs_dominant(self):

        """ Get the dominant production process. """

        idx = self._xs.index(max(self._xs))
        return self._p1[idx], self._p2[idx]

    def get_xs_incl(self):

        """ Get inclusive cross section. """

        return sum(self._xs)

    def get_xs_strong(self):

        """ Get strong cross section. """

        xs_strong = 0.
        for idx, xs in enumerate(self._xs):
            if self._is_strong(self._p1[idx]) and \
               self._is_strong(self._p2[idx]):
                xs_strong += xs

        return xs_strong

    def get_xs_particle(self, id_particle_1, id_particle_2=-1.):

        """ Get cross section for particle with id id_particle. """

        # If id_particle_2 is not defined, set it to id_particle_1
        if id_particle_2 < 0:
            id_particle_2 = id_particle_1

        for idx, xs in enumerate(self._xs):
            if self._p1[idx] == id_particle_1 and \
               self._p2[idx] == id_particle_2:
                return xs

        return 0.
