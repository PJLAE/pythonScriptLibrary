#! /usr/bin/python36
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
#[]  Script: plat4rm.py                                                        []
#[]  Script Language: Python 3.6(.4)                                           []
#[]  Description: This class can be used to retrieve platform specific         []
#[]               information from the underlying system.                      []
#[]  Author: Paul J. Laue                                                      []
#[]  Created: March 1, 2018 10:03:00 AM                                    []
#[] ========================================================================== []
#[]  CHANGE LOG                                                                []
#[]  ----------                                                                []
#[]                                                                            []
#[] ========================================================================== []
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
import platform
import sys

class Platform:
    """
    This class returns information from the underlying system using the
    platform module.
    """
    def __init__(self):
        """
        Creates a new empty Platform object.
        """
        
    def isPlatform64Bits(self):
        """
        Determines whether the underlying platform is 64-bit compatible.
        """
        return sys.maxsize > 2**32
    
    def getHostName(self):
        """
        Returns the name of the computer used to run this program.
        """
        return platform.node()
    
    def getProcessor(self):
        """
        Returns processor name.
        """ 
        return platform.processor()
    
    def getOSType(self):
        """
        Returns the operating system type
        """
        return platform.system()
    
    def getMachineType(self):
        """
        Returns the machine type.
        """
        return platform.machine()
    
    def getOSVersion(self):
        """
        Returns the operating system version.
        """
        return platform.version()
    
    def getOSReleaseNumber(self):
        """
        Returns the operating system release number.
        """
        return platform.release()
    
if __name__ == "__main__":
    p = Platform()
    print("Machine Name: {}".format(p.getHostName()))
    print("Machine Type: {}".format(p.getMachineType()))
    print("Is 64-bit: {}".format(p.isPlatform64Bits()))
    print("OS Type: {}".format(p.getOSType()))
    print("OS Release: {}".format(p.getOSReleaseNumber()))
    print("OS Version: {}".format(p.getOSVersion()))
    print("Processor: {}".format(p.getProcessor()))