#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__title__ = 'VNA tester'
__logo__ = 'JD soft'
__author__ = 'joel.daricou@cern.ch'
__version__ = ' 2019 V.1.0'

plot_names = [ [ ['S21 - delay group', 'GHz', 'nS'],
                 ['S21 - dB Mag', 'GHz', 'dB'],
                 ['S11 - SWR', 'GHz', 'mU'],
                 ['S22 - SWR', 'GHz', 'mU'],
                 ['S11 - Z(Ω)', 'nS', 'Ω']],

               [ ['S21 - TDR', 'nS', 'U'],
                 ['S11 - TDR', 'nS', 'U']]]

instrument_address = ['', 'TCPIP::CFO-MD-BQPVNA1::INSTR', 'TCPIP::VNA-ZNB8-BI-QP::INSTR', 'TCPIP::VNA-ZNB4-BI-QP::INSTR']

test_name = ['Test', 'Feedthrough', 'Pick_up']

directory_name = 'Automatic_tests'
