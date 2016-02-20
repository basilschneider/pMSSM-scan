#!/usr/bin/env python2

""" Make a mass scan for different SUSY particle masses with SUSYHIT and
    calculates branching ratios to various final states. """

from os import system
from re import sub, subn, search
# pylint: disable=no-name-in-module
from itertools import dropwhile, takewhile, ifilterfalse, tee, product
from functools import reduce
from cmath import isnan
from Logger import LGR
from MassScanPlots import MassScanPlots
from ToolboxHelper import get_lst_entry_default


class MassScan(object):  # pylint: disable=too-many-instance-attributes

    """ Make a mass scan for different SUSY particle masses with SUSYHIT and
    calculates branching ratios to various final states. """

    # Flags what to calculate
    _calc_masses = True
    _calc_xs = True
    _calc_br = True
    _calc_mu = True

    # Define ID's of particles
    _id_gluino = 1000021
    _id_neutralino1 = 1000022
    _id_neutralino2 = 1000023
    _id_chargino1 = 1000024
    _id_smhiggs = 25

    # Masses of particles
    _m_gluino = -1.
    _m_neutralino1 = -1.
    _m_neutralino2 = -1.
    _m_chargino1 = -1.
    _m_smhiggs = -1.

    # Cross-sections
    _xs13_incl = -1.
    _xs13_strong = -1.
    _xs13_gluinos = -1.
    _xs8_incl = -1.
    _xs8_strong = -1.

    # Signal strength
    _mu = 0.

    # Directory where SUSYHIT is installed
    _dir_susyhit = '/uscms/home/bschneid/nobackup/pkg/install/'
    _dir_susyhit += 'susyhit-1.5-suspect-2.4.3'
    # Define SUSYHIT option, this should be the same as in susyhit.in:
    # 1 for SuSpect-HDECAY-SDECAY
    # 2 for SDECAY-HDECAY
    # Simply changing this value here won't work right now
    _susyhit_option = 1

    # Define parameter x
    l_prmtr_x = [200., 350.]
    _prmtr_id_x = 3
    _l_prmtr_x_add = {}

    # Define parameter y
    l_prmtr_y = [300.]
    _prmtr_id_y = 23
    _l_prmtr_y_add = {}

    # Track errors, we still want to fill all lists, otherwise the
    # binning will be screwed up
    _error = False

    # Dictionary for decay modes;
    # The SM decays are filled by hand
    # The SUSY decays are filled on the fly when needed,
    # based on the SUSYHIT output file
    _d_sm = {}
    _d_susy = {}

    # List of particles
    _l_jets = [1, 2, 3, 4, 5, 21, 111, 211]
    _l_leptons = [11, 13]
    _l_met = [12, 14, 16, 1000022]
    _l_photon = [22]
    # Unknown particles are ignored
    # (999 is a dummy particle, if decay modes are not known)
    _l_unknown = [999]
    _l_final_states = _l_jets + _l_leptons + _l_met + _l_photon + _l_unknown
    _l_strong = [1000001, 1000002, 1000003, 1000004, 1000005, 1000006,
                 2000001, 2000002, 2000003, 2000004, 2000005, 2000006,
                 1000021]

    # Branching ratios below this threshold are skipped (to save time)
    _threshold = 0.05

    def set_parameter(self, prmtr_id_x, prmtr_id_y):

        """ Set variable parameters x and y. """

        self._prmtr_id_x = prmtr_id_x
        self._prmtr_id_y = prmtr_id_y

    def set_parameter_add_x(self, prmtr_id_x, offset):

        """ Set additional parameters to the same value as x but with an
        offset. """

        self._l_prmtr_x_add[prmtr_id_x] = offset

    def set_parameter_add_y(self, prmtr_id_x, offset):

        """ Set additional parameters to the same value as y but with an
        offset. """

        self._l_prmtr_y_add[prmtr_id_x] = offset

    def _get_susyhit_filename(self):

        """ Get SUSYHIT filename as hardcoded in SUSYHIT. """

        if self._susyhit_option == 1:
            return 'suspect2_lha'
        elif self._susyhit_option == 2:
            return 'slhaspectrum'
        else:
            raise ValueError('susyhit_option is neither 1 nor 2.')

    def _set_parameter_slha(self, idx, parameter):

        """ Set parameter in SUSYHIT input file. """

        LGR.debug('Set index %s to %s in SLHA.', idx, parameter)
        # Set regular expressions in SLHA file
        slha_in = '^ {} '.format(idx)
        slha_out = ' {} '.format(idx)

        # Read file
        with open('{}/{}.in'.format(self._dir_susyhit,
                                    self._get_susyhit_filename()), 'r') as f_in:
            lines = f_in.readlines()

        # Make changes and overwrite file
        with open('{}/{}.in'.format(self._dir_susyhit,
                                    self._get_susyhit_filename()), 'w') as f_in:
            has_replacement = False
            for line in lines:
                t_new = subn('{}.*'.format(slha_in),
                             '{}{}'.format(slha_out, parameter), line)
                if t_new[1] > 0:
                    LGR.debug('Replaced "%s" with "%s" in input file.',
                              line.rstrip(), t_new[0].rstrip())
                    has_replacement = True
                f_in.write(t_new[0])
            if not has_replacement:
                raise RuntimeError('No replacement in SUSYHIT input file has '
                                   'been done.')

    def _set_masses(self, id_particle, m_particle):

        """ Set masses in SUSYHIT input file. """

        # Set regular expressions in SLHA file
        slha = '   {}    '.format(id_particle)

        # Read file
        with open('{}/{}.in'.format(self._dir_susyhit,
                                    self._get_susyhit_filename()), 'r') as f_in:
            lines = f_in.readlines()

        # Make changes and overwrite file
        with open('{}/{}.in'.format(self._dir_susyhit,
                                    self._get_susyhit_filename()), 'w') as f_in:
            for line in lines:
                f_in.write(sub('{}.*'.format(slha),
                               '{}{}'.format(slha, m_particle), line))

    def _run_external(self, name, cmd):  # pylint: disable=no-self-use

        """ Run external software, such as SUSYHIT or SModelS. """

        # If logging level is not set to debug, suppress output
        LGR.debug('Output from %s:', name)
        if LGR.getEffectiveLevel() > 10:
            cmd += ' &> /dev/null'
        # Logic inverted: bash success (0) is python failure
        if system(cmd):
            raise RuntimeError('Could not run {}.'.format(name))

    def _check_susyhit_output(self):

        """ Check SUSYHIT output file for errors. """

        line_warning = 2
        with open('{}/suspect2.out'
                  .format(self._dir_susyhit), 'r') as f_suspect2:
            for line in f_suspect2:
                if line_warning == 0:
                    errorline = line.split('.')
                    errorline.pop()
                    for err in errorline:
                        if err != '' and int(err) != 0:
                            LGR.warning('SUSYHIT reports an error.')
                            return False
                if line_warning != 2:
                    line_warning -= 1
                if line.startswith('STOP'):
                    LGR.warning('SUSYHIT reports an error: %s', line.rstrip())
                    return False
                if line.startswith('Warning'):
                    line_warning -= 1
        return True

    def _fill_dict_sm(self):

        """ Add SM decays to dictionary. """

        # Tau
        self._d_sm[15] = [[.2552, [-211, 111, 16]],
                          [.1153, [-211, 16]],
                          [.0952, [-211, 111, 111, 16]],
                          [.1520, [-211, -211, 211, 16]],
                          [.1783, [11, -12, 16]],
                          [.1741, [13, -14, 16]]]
        # Z
        self._d_sm[23] = [[.03363, [11, -11]],
                          [.03366, [13, -13]],
                          [.03370, [15, -15]],
                          [.2, [12, -12]],
                          [.6991, [4, -4]]]
        # W
        self._d_sm[24] = [[.1071, [11, -12]],
                          [.1063, [13, -14]],
                          [.1138, [15, -16]],
                          [.6741, [3, -4]]]

    def _fill_dict_susy(self, id_particle):

        """ Translate SUSYHIT output into python dictionaries. The format of the
        dictionary is:
        dict[id_particle] = [
                                [prob., [child1, child2, ...]],
                                [prob., [child1, child2, ...]],
                                ...
                            ] """

        # Open SUSYHIT output file
        with open('{}/susyhit_slha.out'
                  .format(self._dir_susyhit)) as f_susyhit_out:
            # Select range to be read from file
            f_susyhit_out_start = dropwhile(lambda l: not
                                            search('^DECAY *{}'.format
                                                   (abs(id_particle)), l),
                                            f_susyhit_out)
            f_susyhit_out_range = takewhile(lambda l: not search('^# *PDG', l),
                                            f_susyhit_out_start)

            # LGR.debug('Range selected from SUSYHIT output file for particle '
            #           '%s:', id_particle)

            # List of all decays
            list_decays = []
            # Loop over selected range and filter out comments
            for line in ifilterfalse(lambda l: search('^ *#|^DECAY', l),
                                     f_susyhit_out_range):
                # LGR.debug(line.rstrip())

                # Split line into list, format is
                # [prob., # of childs, child1, child2, ..., comments]
                list_line_str_comments = line.rstrip().split()
                # LGR.debug('list: %s', list_line_str_comments)

                # Strip all comments from list_line_comments
                list_line_str = list(takewhile(lambda m:
                                               not str(m).startswith('#'),
                                               list_line_str_comments))
                # LGR.debug('list stripped from comments: %s', list_line_str)
                del list_line_str_comments

                # list_line_str needs to have length of at least 4, otherwise
                # something's wrong with the input
                if len(list_line_str) < 3:
                    raise IndexError('list_line_str {} needs to have at least '
                                     '4 elements. Something seems to be wrong '
                                     'with the input.'.format(list_line_str))

                # Convert first element (branching ratio) to float
                # and other elements (number of daughter particles and particle
                # ID's) to integers
                list_line = []
                list_line.append(float(list_line_str[0]))
                list_line.append([int(x) for x in list_line_str[1:]])
                # LGR.debug('list as numbers: %s', list_line)
                del list_line_str

                # According to SLHA format, second number per line should be
                # number of daughter particles
                if list_line[1][0]+1 != len(list_line[1]):
                    raise IndexError('According to SLHA format, second number '
                                     'per line should be number of daugher '
                                     'particles. Something seems to be wrong '
                                     'with the input.')

                # Once we checked for consistency, we can remove list_line[1],
                # since it is redundant
                del list_line[1][0]

                if isnan(list_line[0]):
                    LGR.warning('Some decays have a branching ratio of "NaN" '
                                'in the SUSYHIT output file. These decays are '
                                'skipped.')
                    continue

                # Fill list of decays
                list_decays.append(list_line)
                del list_line

            # Check if list of decays is empty
            if not list_decays:
                # If it is a SM particle, it probably needs to be filled by
                # hand, if it is a SUSY particle, it will be ignored
                #if abs(id_particle) < 1000000:
                #    raise IndexError('SM particle {} could not be found in '
                #                     'dictionary. Maybe it needs to be filled'
                #                     ' by hand?'.format(id_particle))

                # If the particle has no known decay modes, according to
                # SUSYHIT, then we define its decay to 100 % into the unknown
                # (and ignored) particle 999 (which is a final state)
                list_decays.append([1., [999]])
                LGR.warning('Added particle %s to list of ignored particles. '
                            'It does not seem to have any decay modes in the '
                            'SUSYHIT output file.', id_particle)

            # Loop over list_decays to print debug information and sum up
            # branching ratios
            sum_br = 0
            for list_decay in list_decays:
                sum_br += list_decay[0]
                LGR.debug('list_decay: %s', list_decay)

            # Fill dictionary
            self._d_susy[abs(id_particle)] = list_decays
            LGR.info('Filled decay modes from particle with ID %s into '
                     'dictionary.', id_particle)

    def _partition(self, pred, iterable):  # pylint: disable=no-self-use

        """ Use a predicate to partition entries into false entries and true
        entries:
        partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
        (Direct from the recipes in itertools documentation) """

        tee1, tee2 = tee(iterable)
        return ([item for item in tee1 if not pred(item)],
                [item for item in tee2 if pred(item)])

    def _prob_tree(self, id_particle, visited=frozenset()):

        """ Generator of all end points of the probability tree contained
        in d_susy, starting with id_particle """

        # Check if the node has already been visited (which would lead to
        # circular reference, infinite loop)
        if id_particle in visited:
            raise RuntimeError('Branch already visited: {}'
                               .format(id_particle))

        # If id_particle can be found in d_sm, use this dictionary, otherwise
        # use d_susy
        if abs(id_particle) in self._d_sm:
            dct = self._d_sm
        else:
            dct = self._d_susy

        # Fill dictionary if not done already
        # id_particle should *never* be a final state here
        if abs(id_particle) not in dct:
            self._fill_dict_susy(id_particle)

        for prob, path in dct[abs(id_particle)]:
            # Skip if below threshold
            if prob < self._threshold:
                continue
            # Divide sample in final states and non final states
            final, non_final = [tuple(x) for x in self._partition
                                (lambda y: not self._is_final(y), path)]
            if non_final:
                visited = visited.union((id_particle,))
                for node in product(*[self._prob_tree(x, visited)
                                      for x in non_final]):
                    new_prob, new_path = reduce(lambda acum, new:
                                                (acum[0]*new[0],
                                                 acum[1]+new[1]),
                                                node, (prob, tuple()))
                    yield new_prob, final + new_path
            else:
                yield prob, final

    def _get_brs(self, id_parent):  # pylint: disable=too-many-locals

        """ Get probabilites for branching into one, two, ... leptons and jets.
        This includes the combinatorics from 2 parent particles. """

        br_leptons_1leg = []
        br_jets_1leg = []
        br_photons_1leg = []

        LGR.debug('Branching ratios for particle %s:', id_parent)

        # Loop over all decay modes
        for list_decay in self._prob_tree(id_parent):

            LGR.debug('list_decay: %s', list_decay)

            br_single = list_decay[0]

            # Check if we have unknown particles in the final state
            has_unknowns = False

            # Calculate number of particles for specific decay mode
            no_leptons = 0
            no_jets = 0
            no_photons = 0
            for id_particle in list_decay[1]:
                if self._is_unknown(id_particle):
                    has_unknowns = True
                no_leptons += self._is_lepton(id_particle)
                no_jets += self._is_jet(id_particle)
                no_photons += self._is_photon(id_particle)

            # Calculate total branching ratio for consistency;
            # this number will not exactly add up to 1, since rare decay modes
            # are missing and due to obnoxious python rounding errors
            if has_unknowns:
                continue

            # Make sure lists are long enough
            self._expand_list(br_leptons_1leg, no_leptons)
            self._expand_list(br_jets_1leg, no_jets)
            self._expand_list(br_photons_1leg, no_photons)

            # Fill branching ratio
            br_leptons_1leg[no_leptons] += br_single
            br_jets_1leg[no_jets] += br_single
            br_photons_1leg[no_photons] += br_single

        LGR.debug('Branching ratios into leptons: %s', br_leptons_1leg)
        LGR.debug('Branching ratios into jets: %s', br_jets_1leg)
        LGR.debug('Branching ratios into photons: %s', br_photons_1leg)
        LGR.debug('Total branching ratio: %s', sum(br_leptons_1leg))

        # Create list with right length
        br_leptons_2leg = [0]*((2*len(br_leptons_1leg))-1)
        br_jets_2leg = [0]*((2*len(br_jets_1leg))-1)
        br_photons_2leg = [0]*((2*len(br_jets_1leg))-1)

        # Combinatorics going from one leg to two legs
        for idx_l1, br_l1 in enumerate(br_leptons_1leg):
            for idx_l2, br_l2 in enumerate(br_leptons_1leg):
                br_leptons_2leg[idx_l1+idx_l2] += br_l1*br_l2

        for idx_j1, br_j1 in enumerate(br_jets_1leg):
            for idx_j2, br_j2 in enumerate(br_jets_1leg):
                br_jets_2leg[idx_j1+idx_j2] += br_j1*br_j2

        for idx_l1, br_l1 in enumerate(br_photons_1leg):
            for idx_l2, br_l2 in enumerate(br_photons_1leg):
                br_photons_2leg[idx_l1+idx_l2] += br_l1*br_l2

        # If total branching ratio (for both legs) is under a certain
        # threshold, throw a warning; this can have many reasons, like unknown
        # (ignored) particle decays, or thresholds to limit computing time
        if sum(br_leptons_2leg) < .9:
            LGR.warning('The defined threshold led to a total branching '
                        'ratio of %s. You might want to consider lowering the '
                        'threshold.', sum(br_leptons_2leg))

        LGR.debug('Branching ratios into leptons (one leg): %s',
                  br_leptons_1leg)
        LGR.debug('Branching ratios into leptons (two legs): %s',
                  br_leptons_2leg)
        LGR.debug('Branching ratios into jets (one leg): %s', br_jets_1leg)
        LGR.debug('Branching ratios into jets (two legs): %s', br_jets_2leg)
        return br_leptons_2leg, br_jets_2leg, br_photons_2leg

    def _expand_list(self, lst, idx, val=0.):  # pylint: disable=no-self-use

        """ Expand list so it has at least idx entries. """

        while len(lst) <= idx:
            lst.append(val)

    def _is_final(self, id_particle):

        """ Return if id_particle is considered final, i.e. a final state
        particle or an ignored particle. """

        return self._is_final_state(abs(id_particle))

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

    def _skip_point(self, coordinate_x,  # pylint: disable=no-self-use
                    coordinate_y):

        """ Throw warning that point (x/y) will be skipped. """

        self._error = True
        LGR.warning('Skip point (%4d/%4d).', coordinate_x, coordinate_y)

    def _fill_lists(self, lst_in, lst_outs, default=0):  # pylint: disable=no-self-use

        """ Append list lst_in to list of lists lst_outs:
        lst_in = [0, 1]
        lst_outs[0] = [..., 0]
        lst_outs[1] = [..., 1]
        lst_outs[2] = [..., default]
        ... """

        for idx, lst_out in enumerate(lst_outs):
            lst_out.append(get_lst_entry_default(lst_in, idx, default))

    def _get_xs_all(self):

        """ Get all cross-sections. """

        LGR.debug('Get cross-sections:')

        self._xs13_incl, self._xs13_strong = self._get_xs_incl(13)
        self._xs8_incl, self._xs8_strong = self._get_xs_incl(8)
        self._xs13_gluinos = self._get_xs(13, self._id_gluino)

    def _get_xs_incl(self, com):

        """ Get inclusive cross-section. """

        # Regex to be searched in SLHA file
        if com == 13:
            regex_xs = r'XSECTION *1\.30E\+04 *2212 2212'
        elif com == 8:
            regex_xs = r'XSECTION *8\.00E\+03 *2212 2212'
        else:
            raise ValueError('Only cross-sections of 8 or 13 TeV are allowed.')

        xs_incl = 0.
        xs_strong = 0.
        with open('{}/susyhit_slha.out'
                  .format(self._dir_susyhit), 'r') as f_susyhit:
            found_xsec = False
            strong_xsec = False
            for line in f_susyhit:
                if found_xsec:
                    xs_incl += float(line.split()[6])
                    found_xsec = False
                    if strong_xsec:
                        xs_strong += float(line.split()[6])
                        strong_xsec = False
                # If the xs matches, set bool, next line will have the xs
                if search(regex_xs, line):
                    found_xsec = True
                    # Check if strong production
                    if self._is_strong(float(line.split()[5])) and \
                       self._is_strong(float(line.split()[6])):
                        strong_xsec = True

        # Multiply by 1000. to get cross-section in fb
        return 1000.*xs_incl, 1000.*xs_strong

    def _get_xs(self, com, id_particle_1, id_particle_2=-1.):

        """ Get specific cross-section. """

        # If id_particle_2 is not defined, set it to id_particle_1
        if id_particle_2 < 0:
            id_particle_2 = id_particle_1

        # Regex to be searched in SLHA file
        if com == 13:
            regex_xs = r'XSECTION *1\.30E\+04 *2212 2212 2 {} {}' \
                       .format(id_particle_1, id_particle_2)
        elif com == 8:
            regex_xs = r'XSECTION *8\.00E\+03 *2212 2212 2 {} {}' \
                       .format(id_particle_1, id_particle_2)
        else:
            raise ValueError('Only cross-sections of 8 or 13 TeV are allowed.')

        with open('{}/susyhit_slha.out'
                  .format(self._dir_susyhit), 'r') as f_susyhit:
            found_xsec = False
            for line in f_susyhit:
                if found_xsec:
                    xs_incl = float(line.split()[6])
                    LGR.debug('Found XS %s for particles %s and %s from line '
                              '%s.', xs_incl, id_particle_1, id_particle_2,
                              line.rstrip())
                    # Multiply by 1000. to return cross-section in fb
                    return 1000.*xs_incl
                # If the xs matches, set bool, next line will have the xs
                if search(regex_xs, line):
                    LGR.debug(line.rstrip())
                    found_xsec = True

        # If no cross-section was found, return 0
        return 0.

    def _get_mu(self):  # pylint: disable=no-self-use

        """ Get excluded observed signal strength from SModelS output file. """

        with open('smodels_summary.txt', 'r') as f_smodels:
            for line in f_smodels:
                if line.startswith('The highest r value is'):
                    return float(line.rstrip().split()[-1])
        return 0.

    def _get_masses(self):

        """ Calculates masses of SUSY particles and performs some sanity
        checks. """

        self._m_gluino = self._get_m(self._id_gluino)
        self._m_neutralino1 = self._get_m(self._id_neutralino1)
        self._m_neutralino2 = self._get_m(self._id_neutralino2)
        self._m_chargino1 = self._get_m(self._id_chargino1)
        self._m_smhiggs = self._get_m(self._id_smhiggs)

        # Helper lists for following checks
        l_masses = [self._m_gluino, self._m_neutralino1,
                    self._m_neutralino2, self._m_chargino1]
        l_names = ['Gluino', 'Neutralino 1', 'Neutralino 2', 'Chargino 1']

        # Check that N1 is LSP
        if min(l_masses) != self._m_neutralino1:
            LGR.warning('LSP is %s.', l_names[l_masses.index(min(l_masses))])
            return False

        # Check that no mass is negative (is that needed?)
        # if min(l_masses) < 0.:
        #     for val in filter(lambda l: l<0., l_masses):
        #         LGR.warning('%s has negative mass.',
        #                     l_names[l_masses.index(val)])
        #     return False

        return True

    def _get_m(self, id_particle):

        """ Return mass of particle with ID id_particle. """

        with open('{}/susyhit_slha.out'
                  .format(self._dir_susyhit), 'r') as f_susyhit:
            for line in f_susyhit:
                if search('^ *{}'.format(id_particle), line):
                    mass = float((line.split())[1])
                    LGR.debug('Found mass %s for particle %s from line %s.',
                              mass, id_particle, line.rstrip())
                    return abs(mass)

    def set_threshold(self, threshold):

        """ Set threshold under which branching ratios are ignored. The larger
        this value, the more precise, but the slower the computation. """

        self._threshold = threshold

    def do_scan(self):  # pylint: disable=too-many-branches,too-many-statements

        """ Loops over the different mass combinations and calls appropriate
        functions to set masses in the SUSYHIT input file and to fill the
        python dictionary. """

        # Make backup SUSYHIT input file
        system('mv {}/{}.in{{,.orig}}'.format(self._dir_susyhit,
                                              self._get_susyhit_filename()))

        # Copy template input file
        system('cp {}.template {}/{}.in'.format(self._get_susyhit_filename(),
                                                self._dir_susyhit,
                                                self._get_susyhit_filename()))

        # Fill SM dictionary
        self._fill_dict_sm()

        # # Calculate total number of different mass combinations
        # total = len(M_GLUINOS) * len(M_CHARGINOS1) * len(M_NEUTRALINOS1)
        total = len(self.l_prmtr_x) * len(self.l_prmtr_y)

        # Define counter to count from 1 to total
        counter = 0

        # Create MassScanPlots object for plotting
        plots = MassScanPlots()

        # Loop over all mass combinations
        # for m_gluino in M_GLUINOS:
        #     for m_chargino_diff in M_CHARGINOS1:
        #         for m_neutralino_diff in M_NEUTRALINOS1:
        for prmtr_x in self.l_prmtr_x:
            for prmtr_y in self.l_prmtr_y:

                # Clear SUSY dictionary (SM can stay)
                self._d_susy.clear()

                counter += 1

                # Reset error
                self._error = False

                LGR.info('Processing mass combination %3d of %3d: (%4d/%4d).',
                         counter, total, prmtr_x, prmtr_y)

                # # Calculate chargino and neutralino masses
                # m_chargino1 = m_gluino - m_chargino_diff
                # m_neutralino2 = m_chargino1
                # m_neutralino1 = m_chargino1 - m_neutralino_diff

                # LGR.debug('m_g = %4d  -  m_c1 = %4d  -  m_n1 = %4d',
                #           m_gluino, m_chargino1, m_neutralino1)
                LGR.debug('prmtr_x = %4d  -  mu = %4d', prmtr_x, prmtr_y)

                # # Set masses in SUSYHIT input file
                # _set_masses(id_gluino, m_gluino)
                # _set_masses(id_chargino1, m_chargino1)
                # _set_masses(id_neutralino2, m_neutralino2)
                # _set_masses(id_neutralino1, m_neutralino1)
                self._set_parameter_slha(self._prmtr_id_x, prmtr_x)
                self._set_parameter_slha(self._prmtr_id_y, prmtr_y)
                for key, value in self._l_prmtr_x_add.iteritems():
                    # Some combinations are concatenated for axis labeling
                    if key == 414243:
                        for newkey in range(41, 44):
                            self._set_parameter_slha(newkey, prmtr_x+value)
                    elif key == 444546474849:
                        for newkey in range(44, 50):
                            self._set_parameter_slha(newkey, prmtr_x+value)
                    else:
                        self._set_parameter_slha(key, prmtr_x+value)
                for key, value in self._l_prmtr_y_add.iteritems():
                    # Some combinations are concatenated for axis labeling
                    if key == 414243:
                        for newkey in range(41, 44):
                            self._set_parameter_slha(newkey, prmtr_y+value)
                    elif key == 444546474849:
                        for newkey in range(44, 50):
                            self._set_parameter_slha(newkey, prmtr_y+value)
                    else:
                        self._set_parameter_slha(key, prmtr_y+value)

                # Set the plot axis labels
                plots.set_axis(self._prmtr_id_x, self._prmtr_id_y,
                               self._l_prmtr_x_add, self._l_prmtr_y_add)

                # Fill the coordinates
                plots.coordinate_x.append(prmtr_x)
                plots.coordinate_y.append(prmtr_y)

                # Run SUSYHIT
                self._run_external('SUSYHIT', 'cd {} && ./run'
                                   .format(self._dir_susyhit))
                if not self._check_susyhit_output():
                    self._skip_point(prmtr_x, prmtr_y)

                if not self._error and self._calc_masses:
                    # Get particle masses
                    if not self._get_masses():
                        self._skip_point(prmtr_x, prmtr_y)

                # Calculate cross-section with SModelS
                if not self._error and (self._calc_xs or self._calc_mu):
                    # 8 TeV cross-sections to check if the model is already
                    # excluded and 13 TeV cross-sections for cross-sections
                    # itself
                    for com in [8, 13]:
                        self._run_external('SModelS', 'runTools xseccomputer '
                                           '-p -s {} -f {}/susyhit_slha.out'
                                           .format(com, self._dir_susyhit))
                    if self._calc_xs:
                        self._get_xs_all()

                # Move SUSYHIT output
                if not self._error:
                    system('cp {}/susyhit_slha.out susyhit_slha_{}_{}.out'
                           .format(self._dir_susyhit, prmtr_x, prmtr_y))

                # Check if models are already excluded
                if not self._error and self._calc_mu:
                    self._run_external('SModelS', 'runSModelS '
                                       '-o smodels_summary.txt '
                                       '-f {}/susyhit_slha.out'
                                       .format(self._dir_susyhit))
                    self._mu = self._get_mu()

                    # Move SModelS output file
                    system('mv smodels_summary.txt smodels_summary_{}_{}.txt'
                           .format(prmtr_x, prmtr_y))

                    LGR.debug('Excluded signal strength: %s', self._mu)

                if not self._error and self._calc_br:
                    # Calculate branching ratios, if threshold is below 1
                    if self._threshold >= 1.:
                        br_leptons, br_jets, br_photons = [0], [0], [0]
                    else:
                        br_leptons, br_jets, br_photons = \
                        self._get_brs(self._id_gluino)

                    if not br_leptons or not br_jets or not br_photons:
                        self._skip_point(prmtr_x, prmtr_y)

                # If there was an error, empty all values
                if self._error:
                    self._xs13_incl = 0.
                    self._xs13_strong = 0.
                    self._xs13_gluinos = 0.
                    self._xs8_incl = 0.
                    self._xs8_strong = 0.
                    self._m_gluino = 0.
                    self._m_neutralino1 = 0.
                    self._m_neutralino2 = 0.
                    self._m_chargino1 = 0.
                    self._m_smhiggs = 0.
                    self._mu = 0.
                    br_leptons = []
                    br_jets = []
                    br_photons = []

                # Plots for masses and mass differences
                if self._calc_masses:
                    plots.m_gluino.append(self._m_gluino)
                    plots.m_neutralino1.append(self._m_neutralino1)
                    plots.m_neutralino2.append(self._m_neutralino2)
                    plots.m_chargino1.append(self._m_chargino1)
                    plots.m_smhiggs.append(self._m_smhiggs)
                    plots.m_diff_g_c1.append(self._m_gluino - self._m_chargino1)
                    plots.m_diff_c1_n1.append(self._m_chargino1 -
                                          self._m_neutralino1)

                # Plots for xs's
                if self._calc_xs:
                    plots.xs13_incl.append(self._xs13_incl)
                    plots.xs8_incl.append(self._xs8_incl)
                    try:
                        plots.xs13_strong.append(self._xs13_strong/self._xs13_incl)
                        plots.xs8_strong.append(self._xs13_strong/self._xs13_incl)
                        plots.xs13_gluinos.append(self._xs13_gluinos/self._xs13_incl)
                        # XS ratio
                        plots.xs13_xs8.append(self._xs13_incl/self._xs8_incl)
                    except ZeroDivisionError:
                        plots.xs13_strong.append(0.)
                        plots.xs8_strong.append(0.)
                        plots.xs13_gluinos.append(0.)
                        # XS ratio
                        plots.xs13_xs8.append(0.)

                # Fill lists per number of object for br plots
                if self._calc_br:
                    self._fill_lists(br_leptons, plots.br_leptons)
                    self._fill_lists(br_jets, plots.br_jets)
                    self._fill_lists(br_photons, plots.br_photons)

                # Plots for signal strength
                if self._calc_mu:
                    plots.mu.append(self._mu)

        # Restore backup SUSYHIT input file
        system('mv {}/{}.in{{.orig,}}'.format(self._dir_susyhit,
                                              self._get_susyhit_filename()))

        # Throw error when no list is filled
        if len(plots.coordinate_x) == 0:
            raise RuntimeError('Nothing to plot.')

        return plots
