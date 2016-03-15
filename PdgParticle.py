#!/usr/bin/env python2

""" Class containing all PDG particle information. """

from Logger import LGR

class PdgParticle(object):

    """ Class containing all PDG particle information. """

    # Define ID's of particles
    _id_gluino = 1000021
    _id_neutralino1 = 1000022
    _id_neutralino2 = 1000023
    _id_neutralino3 = 1000025
    _id_chargino1 = 1000024
    _id_chargino2 = 1000037
    _id_smhiggs = 25
    _id_stop1 = 1000006
    _id_stop2 = 2000006
    _id_sdown_l = 1000001
    _id_sdown_r = 2000001
    _id_sup_l = 1000002
    _id_sup_r = 2000002
    _id_sstrange_l = 1000003
    _id_sstrange_r = 2000003
    _id_scharm_l = 1000004
    _id_scharm_r = 2000004

    # List of particles
    _l_jets = [1, 2, 3, 4, 5, 21, 111, 211]
    _l_leptons = [11, 13]
    _l_met = [12, 14, 16, 1000022]
    _l_photon = [22]
    # Unknown particles are ignored
    # (999 is a dummy particle, if decay modes are not known)
    _l_unknown = [999]
    _l_final_states = _l_jets + \
                      _l_leptons + \
                      _l_met + \
                      _l_photon + \
                      _l_unknown
    _l_strong = [1000001, 1000002, 1000003, 1000004, 1000005, 1000006,
                 2000001, 2000002, 2000003, 2000004, 2000005, 2000006,
                 1000021]

    def _is_final_state(self, id_particle):

        """ Return if id_particle is considered a final state or not. """

        return abs(id_particle) in self._l_final_states

    def _is_jet(self, id_particle):

        """ Return if id_particle is a final state jet or not. """

        # All particles in this list need to be in the final state list as well
        return abs(id_particle) in self._l_jets

    def _is_lepton(self, id_particle):

        """ Return if id_particle is a charged final state lepton or not. """

        # All particles in this list need to be in the final state list as well
        return abs(id_particle) in self._l_leptons

    def _is_met(self, id_particle):

        """ Return if id_particle is undetectable and leads to missing
        transverse momentum. """

        # All particles in this list need to be in the final state list as well
        return abs(id_particle) in self._l_met

    def _is_photon(self, id_particle):

        """ Return if id_particle is final state photon or not. """

        # All particles in this list need to be in the final state list as well
        return abs(id_particle) in self._l_photon

    def _is_unknown(self, id_particle):

        """ Return if id_particle has unknown decays. """

        return abs(id_particle) in self._l_unknown

    def _is_strong(self, id_particle):

        """ Returns if SUSY particle is colored. """

        return abs(id_particle) in self._l_strong
