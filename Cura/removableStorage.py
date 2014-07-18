"""
This module handles detection and clean ejection of removable storage. (Mainly SD cards)
This is OS depended.
On windows it looks for removable storage drives.
On MacOS it specifically looks for SD cards.
On Linux it looks for anything mounted in /media/

The possible removable storages are scanned for in a background thread, the calls used to scan sometimes block
and we do not want the call to getStorageDevices() to block.
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"
import platform
import string
import glob
import os
import time
import subprocess
import threading
try:
    from xml.etree import cElementTree as ElementTree
except:
    from xml.etree import ElementTree

_removable_cache_update_thread = None
_removable_cache = []


def getStorageDevices():
    """
    Return the known list of removable storage devices. Start the monitoring thread if it does not exists yet.
    The returned list contains a tuple with (human-name, path)
    """
    global _removable_cache, _removable_cache_update_thread

    if _removable_cache_update_thread is None:
        _removable_cache_update_thread = threading.Thread(target=_updateCache)
        _removable_cache_update_thread.daemon = True
        _removable_cache_update_thread.start()
    return _removable_cache


def _parseStupidPListXML(e):
    if e.tag == 'plist':
        return _parseStupidPListXML(list(e)[0])
    if e.tag == 'array':
        ret = []
        for c in list(e):
            ret.append(_parseStupidPListXML(c))
        return ret
    if e.tag == 'dict':
        ret = {}
        key = None
        for c in list(e):
            if c.tag == 'key':
                key = c.text
            elif key is not None:
                ret[key] = _parseStupidPListXML(c)
                key = None
        return ret
    if e.tag == 'true':
        return True
    if e.tag == 'false':
        return False
    return e.text


def _findInTree(t, n):
    ret = []
    if type(t) is dict:
        if '_name' in t and t['_name'] == n:
            ret.append(t)
        for k, v in t.items():
            ret += _findInTree(v, n)
    if type(t) is list:
        for v in t:
            ret += _findInTree(v, n)
    return ret


def _updateCache():
    global _removable_cache

    while True:
        time.sleep(1)
        drives = []
        if platform.system() == "Windows":
            from ctypes import windll
            import ctypes
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.uppercase:
                if letter != 'A' and letter != 'B' and bitmask & 1 and windll.kernel32.GetDriveTypeA(letter + ':/') == 2:
                    volume_name = ''
                    name_buffer = ctypes.create_unicode_buffer(1024)
                    if windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(letter + ':/'), name_buffer, ctypes.sizeof(name_buffer), None, None, None, None, 0) == 0:
                        volume_name = name_buffer.value
                    if volume_name == '':
                        volume_name = 'NO NAME'

                    # Check for the free space. Some card readers show up as a drive with 0 space free when there is no card inserted.
                    freeBytes = ctypes.c_longlong(0)
                    if windll.kernel32.GetDiskFreeSpaceExA(letter + ':/', ctypes.byref(freeBytes), None, None) == 0:
                        continue
                    if freeBytes.value < 1:
                        continue
                    drives.append(('%s (%s:)' % (volume_name, letter), letter + ':/'))
                bitmask >>= 1
        elif platform.system() == "Darwin":
            p = subprocess.Popen(['system_profiler', 'SPUSBDataType', '-xml'], stdout=subprocess.PIPE)
            xml = ElementTree.fromstring(p.communicate()[0])
            p.wait()

            xml = _parseStupidPListXML(xml)
            for dev in _findInTree(xml, 'Mass Storage Device'):
                if 'removable_media' in dev and dev['removable_media'] == 'yes' and 'volumes' in dev and len(dev['volumes']) > 0:
                    for vol in dev['volumes']:
                        if 'mount_point' in vol:
                            volume = vol['mount_point']
                            drives.append((os.path.basename(volume), volume + '/'))

            p = subprocess.Popen(['system_profiler', 'SPCardReaderDataType', '-xml'], stdout=subprocess.PIPE)
            xml = ElementTree.fromstring(p.communicate()[0])
            p.wait()

            xml = _parseStupidPListXML(xml)
            for entry in xml:
                if '_items' in entry:
                    for item in entry['_items']:
                        for dev in item['_items']:
                            if 'removable_media' in dev and dev['removable_media'] == 'yes' and 'volumes' in dev and len(dev['volumes']) > 0:
                                for vol in dev['volumes']:
                                    if 'mount_point' in vol:
                                        volume = vol['mount_point']
                                        drives.append((os.path.basename(volume), volume + '/'))
        else:
            for volume in glob.glob('/media/*'):
                if os.path.ismount(volume):
                    drives.append((os.path.basename(volume), volume + '/'))
                elif volume == '/media/'+os.getenv('USER'):
                    for volume in glob.glob('/media/'+os.getenv('USER')+'/*'):
                        if os.path.ismount(volume):
                            drives.append((os.path.basename(volume), volume + '/'))

        _removable_cache = drives


def ejectDrive(driveName):
    if platform.system() == "Windows":
        cmd = [os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'EjectMedia.exe')), driveName]
    elif platform.system() == "Darwin":
        cmd = ["diskutil", "eject", driveName]
    else:
        cmd = ["umount", driveName]

    kwargs = {}
    if subprocess.mswindows:
        su = subprocess.STARTUPINFO()
        su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        su.wShowWindow = subprocess.SW_HIDE
        kwargs['startupinfo'] = su
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    output = p.communicate()

    if p.wait():
        print output[0]
        print output[1]
        return False
    else:
        return True

if __name__ == '__main__':
    print getStorageDevices()
