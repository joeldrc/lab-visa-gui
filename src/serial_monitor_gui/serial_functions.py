#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import string


def scan_serial():
    ports_names = []
    
    try:
        import serial
        import serial.tools.list_ports
        
        """ Scans for serial ports"""        
        ports = (list(serial.tools.list_ports.comports()))
        for index in range(len(ports)):
            ports_names.append(ports[index][0])
    except:
        print('no serial ports connected')

    return ports_names


def simpleParse(mainString, begin_string, end_string ):
    """Searches for a substring between begin_string and end_string"""
    posbegin_string = mainString.find(begin_string) + len(begin_string)
    posend_string = mainString.find(end_string)
    resultado = mainString[posbegin_string:posend_string]
    return resultado


def extract_int_tag(data_arch, tag):
    """ Extracts data from string datos_str, delimited by <tag> y </tag>
        and convets it to integer numbers (list of integers)"""
    str_channel = ''
    begin_string = '<' + tag + '>'
    end_string = '</'+ tag + '>'
    str_parse = simpleParse(data_arch, begin_string, end_string )
    str_channel = str_parse.split(',')

    channel = []
    n = len(str_channel)
    for i in range(n):
        channel.append(int(str_channel[i]))
    return channel


def conv_str_tag(channel, tag):
    """ Convert every channel from int to str, separated by a coma
    and adds tags at the beggining and end. """
    n = len(channel)
    s_channel = '<' + tag + '>'
    for i in range(n-1):
        s_channel = s_channel + str(channel[i]) + ','
    s_channel = s_channel + str(channel[n-1]) + '</'+ tag + '>'
    return s_channel


def grabar(channel_1, channel_2, channel_3, archivo):
    """ Saves X and Y axis data on file archivo"""
    str_channel = ''
    str_channel += conv_str_tag(channel_1, 'L1') + '\n'
    str_channel += conv_str_tag(channel_2, 'L2') + '\n'
    str_channel += conv_str_tag(channel_3, 'L3') + '\n'

    str_aux = ''
    str_aux += '<nd>' + str(data_to_read) + '</nd>' + '\n'
    str_aux += '<sr>' + str(sample_rate) + '<sr>' + '\n'
    #str_aux += '<gn>' + str(ganancia) + '</gn>' + '\n'

    # Write to file
    arch = open(archivo, "w")
    arch.write(str_aux)
    arch.write(str_channel)
    arch.close()
