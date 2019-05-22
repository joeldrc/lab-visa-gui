#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__title__ = 'VNA tester'
__logo__ = 'JD soft'
__author__ = 'joel.daricou@cern.ch 2018'
__version__ = 'V.1.0'

plot_names = [[['S21 - delay group', 'GHz', 'nS'],
               ['S21 - dB Mag', 'GHz', 'dB'],
               ['S11 - SWR', 'GHz', 'mU'],
               ['S22 - SWR', 'GHz', 'mU'],
               ['S11 - Z(Ω)', 'nS', 'Ω']],

              [['S21 - TDR', 'nS', 'U'],
               ['S11 - TDR', 'nS', 'U']]]

figure_names = [['Flanges'],
                ['Pick-Up']]
