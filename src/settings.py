#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__title__ = 'VNA tester'
__logo__ = 'JD'
__author__ = 'joel.daricou@cern.ch'
__version__ = '03.2022 V.1.0'


plot_names = [ [ ['S21 - delay group', 'GHz', 'nS'],
                 ['S21 - dB Mag', 'GHz', 'dB'],
                 ['S11 - SWR', 'GHz', 'mU'],
                 ['S22 - SWR', 'GHz', 'mU'],
                 ['S11 - Z(Ω)', 'nS', 'Ω']],

               [ ['S21 - delay group', 'GHz', 'nS'],
                 ['S21 - dB Mag', 'GHz', 'dB'],
                 ['S11 - SWR', 'GHz', 'mU'],
                 ['S22 - SWR', 'GHz', 'mU'],
                 ['S11 - Z(Ω)', 'nS', 'Ω']],

               [ ['S21 - TDR', 'nS', 'U'],
                 ['S11 - TDR', 'nS', 'U']],

               [ ['S11 - phase', 'GHz', 'deg'],
                 ['S22 - phase', 'GHz', 'deg'],
                 ['S21 - dB Mag', 'GHz', 'dB'],
                 ['S12 - dB Mag', 'GHz', 'dB'],
                 ['S11 - TDR', 'nS', 'U'],
                 ['S22 - TDR', 'nS', 'U']]]


instrument_address = ['', 'TCPIP::localhost::INSTR',
                      'TCPIP::VNA-ZNB4-BI-BP-1::INSTR',
                      'TCPIP::VNA-ZNB4-BI-BP-2::INSTR',
                      'TCPIP::VNA-ZNB8-BI-BP::INSTR',
                      'TCPIP::AGILENTE5071C::INSTR',
                      'TCPIP::BP-WIFI-KEY::INSTR']


# Name of the test you want to run on the instrument
test_name = ['_Read_data_', 'Feedthrough', 'Cables', 'Pick_up', 'Phase_and_transmission', 'Collimators_commissioning']

# Directory in the instrument
directory_name = 'Automatic_tests'

# Number of ports in the instrument
port_number = 2 # change the number of ports .s[num]p
