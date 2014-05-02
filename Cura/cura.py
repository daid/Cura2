#!/usr/bin/python
"""
This page is in the table of contents.
==Overview==
===Introduction===
Cura is a AGPL tool chain to generate a GCode path for 3D printing. Older versions of Cura where based on Skeinforge.
Versions up from 13.05 are based on a C++ engine called CuraEngine.
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

from optparse import OptionParser


def main():
    """
    Main Cura entry point. Parses arguments, and starts GUI or slicing process depending on the arguments.
    """
    from Cura import localization
    localization.setup()

    parser = OptionParser(usage="usage: %prog [options] <filename>.stl")
    parser.add_option("-i", "--ini", action="store", type="string", dest="profileini",
        help="Load settings from a profile ini file")
    parser.add_option("-r", "--print", action="store", type="string", dest="printfile",
        help="Open the printing interface, instead of the normal cura interface.")
    parser.add_option("-p", "--profile", action="store", type="string", dest="profile",
        help="Internal option, do not use!")
    parser.add_option("-s", "--slice", action="store_true", dest="slice",
        help="Slice the given files instead of opening them in Cura")
    parser.add_option("-o", "--output", action="store", type="string", dest="output",
        help="path to write sliced file to")
    parser.add_option("--serialCommunication", action="store", type="string", dest="serialCommunication",
        help="Start commandline serial monitor")

    (options, args) = parser.parse_args()

    from gui.app import CuraApp
    CuraApp().MainLoop()
    CuraApp().finished()

if __name__ == '__main__':
    main()
