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
    from Cura.resources import getDefaultPreferenceStoragePath
    from Cura import preferences
    preferences.loadPreferences(getDefaultPreferenceStoragePath('preferences.ini'))
    localization.setup()

    parser = OptionParser(usage="usage: %prog [options] <filename>.stl")

    (options, args) = parser.parse_args()

    from app import CuraFDMApp
    app = CuraFDMApp()
    app.MainLoop()
    app.finished()
    preferences.savePreferences(getDefaultPreferenceStoragePath('preferences.ini'))

if __name__ == '__main__':
    main()
