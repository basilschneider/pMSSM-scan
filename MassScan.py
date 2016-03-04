#!/usr/bin/env python2

""" Make a mass scan for different SUSY particle masses with SUSYHIT and
    calculates branching ratios to various final states. """

from os import system
from re import sub, subn, search
from itertools import dropwhile, takewhile, ifilterfalse, tee, product
from functools import reduce
from cmath import isnan
from fileinput import input
from Logger import LGR
from ToolboxHelper import get_lst_entry_default
from PdgParticle import PdgParticle
from MassScanPlots import MassScanPlots
from DecayChannel import DecayChannel
from CrossSection import CrossSection


class MassScan(PdgParticle):

    """ Make a mass scan for different SUSY particle masses with SUSYHIT and
    calculates branching ratios to various final states. """

    # Class-level variables

    # Flags what to calculate
    _calc_masses = True
    _calc_xs = True
    _calc_br = True
    _calc_mu = False

    # Directory where SUSYHIT is installed
    _dir_susyhit = '/uscms/home/bschneid/nobackup/pkg/install/'
    _dir_susyhit += 'susyhit-1.5-suspect-2.4.3'
    # Define SUSYHIT option, this should be the same as in susyhit.in:
    # 1 for SuSpect-HDECAY-SDECAY
    # 2 for SDECAY-HDECAY
    # Simply changing this value here won't work right now
    _susyhit_option = 1

    # Define k-factors for separate for strong and weak processes. These are
    # applied to the LO cross sections and have to be calculated separately
    _k_strong = 1.99
    _k_weak = 1.30

    def __init__(self):

        """ Initialization of class and instance variables. """

        # Define parameter x
        self.l_prmtr_x = [200., 350.]
        self._prmtr_id_x = 3
        self._l_prmtr_x_add = {}

        # Define parameter y
        self.l_prmtr_y = [300.]
        self._prmtr_id_y = 23
        self._l_prmtr_y_add = {}

        # Branching ratios below this threshold are skipped (to save time)
        self._threshold = 0.05

        # Masses of particles
        self._m_gluino = -1.
        self._m_neutralino1 = -1.
        self._m_neutralino2 = -1.
        self._m_neutralino3 = -1.
        self._m_chargino1 = -1.
        self._m_stop1 = -1.
        self._m_stop2 = -1.
        self._m_smhiggs = -1.
        self._m_sdown_l = -1.
        self._m_sdown_r = -1.
        self._m_sup_l = -1.
        self._m_sup_r = -1.
        self._m_sstrange_l = -1.
        self._m_sstrange_r = -1.
        self._m_scharm_l = -1.
        self._m_scharm_r = -1.

        # Lifetimes of particles
        self._lt_gluino = -1.
        self._lt_chargino1 = -1.
        self._lt_neutralino2 = -1.

        # Cross-sections
        self._xs13_incl = -1.
        self._xs13_strong = -1.
        self._xs13_gluinos = -1.
        self._xs8_incl = -1.
        self._xs8_strong = -1.

        # Dominant production cross section particles
        self._dom_id1 = -1
        self._dom_id2 = -1

        # Cross-sections
        self._xs13 = CrossSection()
        self._xs8 = CrossSection()

        # Decay channels
        self._dc_gluino = DecayChannel()
        self._dc_chargino1 = DecayChannel()
        self._dc_neutralino2 = DecayChannel()
        self._dc_neutralino3 = DecayChannel()
        self._dc_sdown_l = DecayChannel()
        self._dc_sdown_r = DecayChannel()
        self._dc_sup_l = DecayChannel()
        self._dc_sup_r = DecayChannel()
        self._dc_sstrange_l = DecayChannel()
        self._dc_sstrange_r = DecayChannel()
        self._dc_scharm_l = DecayChannel()
        self._dc_scharm_r = DecayChannel()

        # Branching ratios into particles
        self._br_leptons = []
        self._br_jets = []
        self._br_photons = []

        # Signal strength
        self._mu = 0.

        # Track errors, we still want to fill all lists, otherwise the
        # binning will be screwed up
        self._error = False

        # Dictionary for decay modes;
        # The SM decays are filled by hand
        # The SUSY decays are filled on the fly when needed,
        # based on the SUSYHIT output file
        self._d_sm = {}
        self._d_susy = {}

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

    def _set_parameter_all(self, prmtr_x, prmtr_y):

        """ Set all parameters in the SLHA file. """

        # Some combinations are concatenated for axis labeling
        if self._prmtr_id_x == 4142:
            for newprmtr in range(41, 43):
                self._set_parameter_slha(newprmtr, prmtr_x)
        elif self._prmtr_id_x == 44454748:
            for newprmtr in [44, 45, 47, 48]:
                self._set_parameter_slha(newprmtr, prmtr_x)
        else:
            self._set_parameter_slha(self._prmtr_id_x, prmtr_x)

        if self._prmtr_id_y == 4142:
            for newprmtr in range(41, 43):
                self._set_parameter_slha(newprmtr, prmtr_y)
        elif self._prmtr_id_y == 44454748:
            for newprmtr in [44, 45, 47, 48]:
                self._set_parameter_slha(newprmtr, prmtr_y)
        else:
            self._set_parameter_slha(self._prmtr_id_y, prmtr_y)

        for key, value in self._l_prmtr_x_add.iteritems():
            if key == 4142:
                for newkey in range(41, 43):
                    self._set_parameter_slha(newkey, prmtr_x+value)
            elif key == 44454748:
                for newkey in [44, 45, 47, 48]:
                    self._set_parameter_slha(newkey, prmtr_x+value)
            else:
                self._set_parameter_slha(key, prmtr_x+value)

        for key, value in self._l_prmtr_y_add.iteritems():
            # Some combinations are concatenated for axis labeling
            if key == 4142:
                for newkey in range(41, 43):
                    self._set_parameter_slha(newkey, prmtr_y+value)
            elif key == 44454748:
                for newkey in [44, 45, 47, 48]:
                    self._set_parameter_slha(newkey, prmtr_y+value)
            else:
                self._set_parameter_slha(key, prmtr_y+value)


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

    def _run_external(self, name, cmd,  # pylint: disable=no-self-use
                      check_for_error=True):

        """ Run external software, such as SUSYHIT or SModelS. """

        # If logging level is not set to debug, suppress output
        LGR.debug('Output from %s:', name)
        if LGR.getEffectiveLevel() > 10:
            cmd += ' &> /dev/null'
        # Logic inverted: bash success (0) is python failure
        if system(cmd) and check_for_error:
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
                                (lambda y: not self._is_final_state(y), path)]
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

    def _get_br_all(self):

        """ Get branching fractions into n particles for all production
        processes. """

        self._br_leptons = []
        self._br_jets = []
        self._br_photons = []

        if self._threshold >= 1.:
            self._br_leptons = [0]
            self._br_jets = [0]
            self._br_photons = [0]
        else:
            # Calculate branching ratios, if threshold is below 1
            self._get_brs(self._id_gluino, self._id_gluino)

        if not self._br_leptons or \
           not self._br_jets or \
           not self._br_photons:
            self._skip_point(prmtr_x, prmtr_y)

    def _get_brs(self, id_parent_1, id_parent_2=-1.):

        """ Get probabilites for branching into one, two, ... leptons and jets.
        This includes the combinatorics from 2 parent particles. """

        # If id_parent_2 is not set, set it to same value as id_parent_1
        if id_parent_2 < 0:
            id_parent_2 = id_parent_1

        br_leptons_1leg_1, br_jets_1leg_1, br_photons_1leg_1 = \
            self._get_br_1leg(id_parent_1)

        # Don't call self._get_br_1leg() again if both parent particles are the
        # same
        if id_parent_2 == id_parent_1:
            br_leptons_1leg_2 = br_leptons_1leg_1
            br_jets_1leg_2 = br_jets_1leg_1
            br_photons_1leg_2 = br_photons_1leg_1
        else:
            br_leptons_1leg_2, br_jets_1leg_2, br_photons_1leg_2 = \
                self._get_br_1leg(id_parent_2)

        # Create list with right length
        br_leptons_2leg = [0]*(len(br_leptons_1leg_1)+len(br_leptons_1leg_2)-1)
        br_jets_2leg = [0]*(len(br_jets_1leg_1)+len(br_jets_1leg_2)-1)
        br_photons_2leg = [0]*(len(br_photons_1leg_1)+len(br_photons_1leg_2)-1)

        # Combinatorics going from one leg to two legs
        for idx_l1, br_l1 in enumerate(br_leptons_1leg_1):
            for idx_l2, br_l2 in enumerate(br_leptons_1leg_2):
                br_leptons_2leg[idx_l1+idx_l2] += br_l1*br_l2

        for idx_j1, br_j1 in enumerate(br_jets_1leg_1):
            for idx_j2, br_j2 in enumerate(br_jets_1leg_2):
                br_jets_2leg[idx_j1+idx_j2] += br_j1*br_j2

        for idx_l1, br_l1 in enumerate(br_photons_1leg_1):
            for idx_l2, br_l2 in enumerate(br_photons_1leg_2):
                br_photons_2leg[idx_l1+idx_l2] += br_l1*br_l2

        # If total branching ratio (for both legs) is under a certain
        # threshold, throw a warning; this can have many reasons, like unknown
        # (ignored) particle decays, or thresholds to limit computing time
        if sum(br_leptons_2leg) < .9:
            LGR.warning('The defined threshold led to a total branching '
                        'ratio of %s. You might want to consider lowering the '
                        'threshold.', sum(br_leptons_2leg))

        LGR.debug('Branching ratios into leptons (1st leg): %s',
                  br_leptons_1leg_1)
        LGR.debug('Branching ratios into leptons (2nd leg): %s',
                  br_leptons_1leg_2)
        LGR.debug('Branching ratios into leptons (both legs): %s',
                  br_leptons_2leg)

        self._br_leptons += br_leptons_2leg
        self._br_jets += br_jets_2leg
        self._br_photons += br_photons_2leg

    def _get_br_1leg(self, id_parent):

        """ Get branching ratio into particles for one particle. """

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

        return br_leptons_1leg, br_jets_1leg, br_photons_1leg

    def _expand_list(self, lst, idx, val=0.):  # pylint: disable=no-self-use

        """ Expand list so it has at least idx entries. """

        while len(lst) <= idx:
            lst.append(val)

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

    def _apply_k_factor(self):

        """ Apply K-factor to LO cross sections. The k-factors differ for
        strong and weak production. They have to be calculated separately.  """

        # Use fileinput.input to do inline editing
        found_xsec = False
        strong_xsec = False
        for line in input('{}/susyhit_slha.out'
                          .format(self._dir_susyhit), inplace=True):
            if found_xsec:

                if strong_xsec:
                    k_factor = self._k_strong
                else:
                    k_factor = self._k_weak

                list_line = line.split()
                list_line[6] = str(k_factor*float(list_line[6]))
                line_new = ' '.join(list_line)

                # The print statement is redirected to the file
                print line_new

                found_xsec = False
                strong_xsec = False
                continue

            # If the xs matches, set bool, next line will have the xs
            if search('XSECTION', line):
                found_xsec = True
                # Check if strong production
                if self._is_strong(float(line.split()[5])) and \
                   self._is_strong(float(line.split()[6])):
                    strong_xsec = True

            print line,

    def _get_xs(self):

        """ Get cross sections. """

        self._xs13 = CrossSection()
        self._xs8 = CrossSection()

        # Get cross sections from SLHA, both for 13 and 8 TeV
        self._xs13.get_xs(13, self._dir_susyhit)
        self._xs8.get_xs(8, self._dir_susyhit)

        # Get dominant production process
        self._dom_id1, self._dom_id2 = self._xs13.get_xs_dominant()

        # Get inclusive cross sections
        self._xs13_incl = self._xs13.get_xs_incl()
        self._xs8_incl = self._xs8.get_xs_incl()

        # Get strong cross sections
        self._xs13_strong = self._xs13.get_xs_strong()
        self._xs8_strong = self._xs8.get_xs_strong()

        # Get gluino gluino cross section
        self._xs13_gluinos = self._xs13.get_xs_particle(self._id_gluino)

    def _get_mu(self):  # pylint: disable=no-self-use

        """ Get excluded observed signal strength from SModelS output file. """

        try:
            with open('smodels_summary.txt', 'r') as f_smodels:
                for line in f_smodels:
                    if line.startswith('The highest r value is'):
                        return float(line.rstrip().split()[-1])
        except IOError:
            pass

        return 0.

    def _get_masses(self):

        """ Get masses of SUSY particles. """

        self._m_gluino = self._get_m(self._id_gluino)
        self._m_neutralino1 = self._get_m(self._id_neutralino1)
        self._m_neutralino2 = self._get_m(self._id_neutralino2)
        self._m_neutralino3 = self._get_m(self._id_neutralino3)
        self._m_chargino1 = self._get_m(self._id_chargino1)
        self._m_stop1 = self._get_m(self._id_stop1)
        self._m_stop2 = self._get_m(self._id_stop2)
        self._m_smhiggs = self._get_m(self._id_smhiggs)
        self._m_sdown_l = self._get_m(self._id_sdown_l)
        self._m_sdown_r = self._get_m(self._id_sdown_r)
        self._m_sup_l = self._get_m(self._id_sup_l)
        self._m_sup_r = self._get_m(self._id_sup_r)
        self._m_sstrange_l = self._get_m(self._id_sstrange_l)
        self._m_sstrange_r = self._get_m(self._id_sstrange_r)
        self._m_scharm_l = self._get_m(self._id_scharm_l)
        self._m_scharm_r = self._get_m(self._id_scharm_r)

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

    def _get_lifetimes(self):

        """ Get lifetimes of particles. """

        self._lt_gluino = self._get_lt(self._id_gluino)
        self._lt_chargino1 = self._get_lt(self._id_chargino1)
        self._lt_neutralino2 = self._get_lt(self._id_neutralino2)

    def _get_lt(self, id_particle):

        """ Return lifetime of particle with ID id_particle. """

        with open('{}/susyhit_slha.out'
                  .format(self._dir_susyhit), 'r') as f_susyhit:
            for line in f_susyhit:
                if search('^DECAY *{}'.format(id_particle), line):
                    lifetime = 1./(float((line.split())[2])*1.51926778e24)
                    return lifetime

    def _check_lsp(self):

        """ Check that the LSP is a neutralino1. """

        min_mass = '1e10'

        with open('{}/susyhit_slha.out'
                  .format(self._dir_susyhit), 'r') as f_susyhit:
            for line in f_susyhit:
                # Check for SUSY masses
                if search('^ *[12]000', line):
                    mass = abs(float((line.split())[1]))
                    id_particle = int((line.split())[0])
                    if mass < min_mass:
                        min_mass = mass
                        min_id = id_particle
        if min_id == 1000022:
            return True
        else:
            LGR.warning('LSP is %s', min_id)
            return False

    def set_threshold(self, threshold):

        """ Set threshold under which branching ratios are ignored. The larger
        this value, the more precise, but the slower the computation. """

        self._threshold = threshold

    def _reset(self):

        """ Reset all plotted variables. """

        self._xs13_incl = 0.
        self._xs13_strong = 0.
        self._xs13_gluinos = 0.
        self._xs8_incl = 0.
        self._xs8_strong = 0.
        self._m_gluino = 0.
        self._m_neutralino1 = 0.
        self._m_neutralino2 = 0.
        self._m_neutralino3 = 0.
        self._m_chargino1 = 0.
        self._m_stop1 = 0.
        self._m_stop2 = 0.
        self._m_smhiggs = 0.
        self._m_sdown_l = 0.
        self._m_sdown_r = 0.
        self._m_sup_l = 0.
        self._m_sup_r = 0.
        self._m_sstrange_l = 0.
        self._m_sstrange_r = 0.
        self._m_scharm_l = 0.
        self._m_scharm_r = 0.
        self._lt_gluino = 0.
        self._lt_chargino1 = 0.
        self._lt_neutralino2 = 0.
        self._mu = 0.
        self._dom_id1 = 0
        self._dom_id2 = 0
        self._xs13 = CrossSection()
        self._xs8 = CrossSection()
        self._dc_gluino = DecayChannel()
        self._dc_chargino1 = DecayChannel()
        self._dc_neutralino2 = DecayChannel()
        self._dc_neutralino3 = DecayChannel()
        self._dc_sdown_l = DecayChannel()
        self._dc_sdown_r = DecayChannel()
        self._dc_sup_l = DecayChannel()
        self._dc_sup_r = DecayChannel()
        self._dc_sstrange_l = DecayChannel()
        self._dc_sstrange_r = DecayChannel()
        self._dc_scharm_l = DecayChannel()
        self._dc_scharm_r = DecayChannel()
        self._br_leptons = []
        self._br_jets = []
        self._br_photons = []

    def _get_dcs(self, id_particle):

        """ Fill lists with decays for particle with id particle_id. """

        # Create decay_channel object
        dc_obj = DecayChannel()

        # If particle not yet in dictionary, fill it
        if not id_particle in self._d_susy:
            self._fill_dict_susy(id_particle)

        # Loop over decays
        for decay in self._d_susy[id_particle]:
            dc_obj.fill_dcs(decay)

        return dc_obj

    def _fill_plots(self, plots, prmtr_x, prmtr_y):

        """ Fill all lists in the MassScanPlots object. """

        # Fill the coordinates
        plots.coordinate_x.append(prmtr_x)
        plots.coordinate_y.append(prmtr_y)

        # Plots for masses
        if self._calc_masses:
            plots.m_gluino.append(self._m_gluino)
            plots.m_neutralino1.append(self._m_neutralino1)
            plots.m_neutralino2.append(self._m_neutralino2)
            plots.m_neutralino3.append(self._m_neutralino3)
            plots.m_chargino1.append(self._m_chargino1)
            plots.m_stop1.append(self._m_stop1)
            plots.m_stop2.append(self._m_stop2)
            plots.m_smhiggs.append(self._m_smhiggs)
            plots.m_sdown_l.append(self._m_sdown_l)
            plots.m_sdown_r.append(self._m_sdown_r)
            plots.m_sup_l.append(self._m_sup_l)
            plots.m_sup_r.append(self._m_sup_r)
            plots.m_sstrange_l.append(self._m_sstrange_l)
            plots.m_sstrange_r.append(self._m_sstrange_r)
            plots.m_scharm_l.append(self._m_scharm_l)
            plots.m_scharm_r.append(self._m_scharm_r)

        # Plots for lifetimes
        if self._calc_br:
            plots.lt_gluino.append(self._lt_gluino)
            plots.lt_chargino1.append(self._lt_chargino1)
            plots.lt_neutralino2.append(self._lt_neutralino2)

        # Plots for xs's
        if self._calc_xs:
            plots.xs13_incl.append(self._xs13_incl)
            plots.xs8_incl.append(self._xs8_incl)
            try:
                plots.xs13_strong.append(self._xs13_strong/self._xs13_incl)
                plots.xs8_strong.append(self._xs13_strong/self._xs13_incl)
                plots.xs13_gluinos.append(self._xs13_gluinos/self._xs13_incl)
            except ZeroDivisionError:
                plots.xs13_strong.append(0.)
                plots.xs8_strong.append(0.)
                plots.xs13_gluinos.append(0.)

        # Plots for decay channels
        if self._calc_br:
            plots.dc_gluino.append(self._dc_gluino)
            plots.dc_chargino1.append(self._dc_chargino1)
            plots.dc_neutralino2.append(self._dc_neutralino2)
            plots.dc_neutralino3.append(self._dc_neutralino3)
            plots.dc_sdown_l.append(self._dc_sdown_l)
            plots.dc_sdown_r.append(self._dc_sdown_r)
            plots.dc_sup_l.append(self._dc_sup_l)
            plots.dc_sup_r.append(self._dc_sup_r)
            plots.dc_sstrange_l.append(self._dc_sstrange_l)
            plots.dc_sstrange_r.append(self._dc_sstrange_r)
            plots.dc_scharm_l.append(self._dc_scharm_l)
            plots.dc_scharm_r.append(self._dc_scharm_r)

        # Fill lists per number of object for br plots
        if self._calc_br:
            plots.dom_id1.append(self._dom_id1)
            plots.dom_id2.append(self._dom_id2)
            self._fill_lists(self._br_leptons, plots.br_leptons)
            self._fill_lists(self._br_jets, plots.br_jets)
            self._fill_lists(self._br_photons, plots.br_photons)

        # Plots for signal strength
        if self._calc_mu:
            plots.mu.append(self._mu)

        return plots

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

        # Set the plot axis labels
        plots.set_axis(self._prmtr_id_x, self._prmtr_id_y,
                       self._l_prmtr_x_add, self._l_prmtr_y_add)

        for prmtr_x in self.l_prmtr_x:
            for prmtr_y in self.l_prmtr_y:

                # Clear SUSY dictionary (SM can stay)
                self._d_susy.clear()

                counter += 1

                # Reset error
                self._error = False

                LGR.info('Processing mass combination %3d of %3d: (%4d/%4d).',
                         counter, total, prmtr_x, prmtr_y)

                LGR.debug('prmtr_x = %4d  -  mu = %4d', prmtr_x, prmtr_y)

                self._set_parameter_all(prmtr_x, prmtr_y)

                # Run SUSYHIT
                self._run_external('SUSYHIT', 'cd {} && ./run'
                                   .format(self._dir_susyhit))
                if not self._check_susyhit_output():
                    self._skip_point(prmtr_x, prmtr_y)

                # Check for LSP
                if not self._error and not self._check_lsp():
                    self._skip_point(prmtr_x, prmtr_y)

                # Get particle masses
                if not self._error and self._calc_masses:
                    self._get_masses()

                # Get particle lifetimes
                if not self._error and self._calc_br:
                    self._get_lifetimes()

                # Calculate cross-section with SModelS
                if not self._error and (self._calc_xs or self._calc_mu):
                    # 8 TeV cross-sections to check if the model is already
                    # excluded and 13 TeV cross-sections for cross-sections
                    # itself
                    for com in [8, 13]:
                        self._run_external('SModelS', 'runTools xseccomputer '
                                           '-p -s {} -f {}/susyhit_slha.out'
                                           .format(com, self._dir_susyhit))

                    # Apply k-factors
                    self._apply_k_factor()

                    if self._calc_xs:
                        self._get_xs()


                # Move SUSYHIT output
                system('cp {}/susyhit_slha.out susyhit_slha_{}_{}.out'
                       .format(self._dir_susyhit, prmtr_x, prmtr_y))
                system('cp {}/suspect2.out suspect2_{}_{}.out'
                       .format(self._dir_susyhit, prmtr_x, prmtr_y))

                # Check if models are already excluded
                if not self._error and self._calc_mu:
                    self._run_external('SModelS', 'timeout 1800 runSModelS '
                                       '-o smodels_summary.txt '
                                       '-f {}/susyhit_slha.out'
                                       .format(self._dir_susyhit), False)
                    self._mu = self._get_mu()

                    # Move SModelS output file
                    system('mv smodels_summary.txt smodels_summary_{}_{}.txt '
                           '2>/dev/null'.format(prmtr_x, prmtr_y))

                    LGR.debug('Excluded signal strength: %s', self._mu)

                # Calculate branching ratios into final states
                if not self._error and self._calc_br:
                    self._get_br_all()

                # Get decay channels
                if not self._error and self._calc_br:
                    self._dc_gluino = self._get_dcs(self._id_gluino)
                    self._dc_chargino1 = self._get_dcs(self._id_chargino1)
                    self._dc_neutralino2 = self._get_dcs(self._id_neutralino2)
                    self._dc_neutralino3 = self._get_dcs(self._id_neutralino3)
                    self._dc_sdown_l = self._get_dcs(self._id_sdown_l)
                    self._dc_sdown_r = self._get_dcs(self._id_sdown_r)
                    self._dc_sup_l = self._get_dcs(self._id_sup_l)
                    self._dc_sup_r = self._get_dcs(self._id_sup_r)
                    self._dc_sstrange_l = self._get_dcs(self._id_sstrange_l)
                    self._dc_sstrange_r = self._get_dcs(self._id_sstrange_r)
                    self._dc_scharm_l = self._get_dcs(self._id_scharm_l)
                    self._dc_scharm_r = self._get_dcs(self._id_scharm_r)

                # If there was an error, empty all values
                if self._error:
                    self._reset()

                plots = self._fill_plots(plots, prmtr_x, prmtr_y)

        # Restore backup SUSYHIT input file
        system('mv {}/{}.in{{.orig,}}'.format(self._dir_susyhit,
                                              self._get_susyhit_filename()))

        # Throw error when no list is filled
        if len(plots.coordinate_x) == 0:
            raise RuntimeError('Nothing to plot.')

        return plots
