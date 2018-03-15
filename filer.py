#! /usr/bin/python36
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
#[]  Script: filer.py                                                          []
#[]  Script Language: Python 3.6(.4)                                           []
#[]  Description: This class provides basic file operations such as:           []
#[]                 1) copy                                                    []
#[]                 2) move                                                    []
#[]                 3) rename                                                  []
#[]                 4) delete                                                  []
#[]                 5) create new directory                                    []
#[]  Author: Paul J. Laue                                                      []
#[]  Created: February 23, 2018 1:20:00 PM                                     []
#[] ========================================================================== []
#[]  CHANGE LOG                                                                []
#[]  ----------                                                                []
#[]                                                                            []
#[] ========================================================================== []
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
import os.path
import shutil
import glob

class Filer:
    """
    This class handles basic file operations such as copy, move, rename, delete using the shutil module.
    """
    def __init__(self):
        """
        Creates an new empty File object.
        """
        self._errMsg = ''
        self._outMsg = ''
        self._srcfilefull = ''
        self._newfilefull = ''
        self._makenewdir = False
    
    def getErrorMsg(self):
        """
        Returns any error messages on the stack.
        
        @return String
        """
        return self._errMsg
    
    def getOutputMsg(self):
        """
        Returns any output messages on the stack.
        
        @return String
        """
        return self._outMsg  
    
    def directoryExists(self, directory):
        """
        Attempts to validate whether a directory exists or not.
        
        @param directory: path to validate if exists or not.
        @type directory: String
        
        @return Boolean
        """
        if directory is None:
            return False
        elif type(directory) == str:            
            return os.path.isdir(directory)
        else:
            return False
    
    def filesExist(self, files):
        """
        Attempts to validate whether files exist or not.
        
        @param files: a list of files to validate
        @type files: List/Sequence
        
        @return Boolean 
        """
        if files is None:
            return False
        elif type(files) == str:
            if not os.path.isfile(files): return False 
        else:
            for fl in files:
                if not os.path.isfile(fl): return False
                
        return True
    
    def searchFilesMatchingPattern(self, pathToSearch, pattern):
        """
        Use glob module to find files matching a particular pattern
        
        @param pathToSearch: path (only) to use in search
        @type pathToSearch: String
        
        @param pattern: pattern to use when searching for file(s)
        @type pattern: String
        
        @return List
        """
        if self.directoryExists(pathToSearch):
            searchfor = os.path.join(pathToSearch, pattern)
            return glob.glob(searchfor)           
        else:
            self._errMsg = "The path to search '{pathToSearch}' does not exist!".format(pathToSearch=pathToSearch)
            
        return None

    def copy(self, pathToSourceFile, sourceFileName, pathToNewFile, newFileName, makeNewPath=False):
        """
        Use shutil module to copy file to a new location.
        
        @param pathToSourceFile: path (only) where source file exists.
        @param type: String
        
        @param sourceFileName: name (only) of source file.
        @type sourceFileName: String
        
        @param pathToNewFile: path (only) where new file should be copied to.
        @type pathToNewFile: String
        
        @param newFileName: name (only) of the new file.
        @type newFileName: String
        
        @param makeNewPath (optional): indicates whether to create the new file path if necessary
        @type makeNewPath: Boolean
        
        @return Boolean
        """
        self._makenewdir = makeNewPath
        self._srcfilefull = os.path.join(pathToSourceFile, sourceFileName)
        self._newfilefull = os.path.join(pathToNewFile, newFileName)
               
        if not self.filesExist(self._srcfilefull):
            self._errMsg = "Source file '{sourceFileName}' at path '{pathToSourceFile}' does not exist or is invalid!".format(sourceFileName=sourceFileName, pathToSourceFile=pathToSourceFile) 
            return False
        
        if not makeNewPath and not self.directoryExists(pathToNewFile):
            self._errMsg = "The path to new file '{pathToNewFile}' must exist!".format(pathToNewFile=pathToNewFile)
            return False
        else:
            self.makeDirectory(pathToNewFile)
        
        # copy file to new location
        try:
            shutil.copy2(self._srcfilefull, self._newfilefull)
        except OSError as oerr:
            self._errMsg = "File '{sourceFileName}' at path '{pathToSourceFile}' could not be copied to path '{pathToNewFile}'!  OSError={oerr}".format(sourceFileName=sourceFileName, pathToSourceFile=pathToSourceFile, pathToNewFile=pathToNewFile, oerr=oerr) 
            return False
        
        return True
    
    def move(self, pathToSourceFile, sourceFileName, pathToNewFile, newFileName, makeNewPath=False):
        """
        Use shutil module to copy file to a new location and delete the original copy.
        
        @param pathToSourceFile: path (only) where source file exists.
        @param type: String
        
        @param sourceFileName: name (only) of source file.
        @type sourceFileName: String
        
        @param pathToNewFile: path (only) where new file should be copied to.
        @type pathToNewFile: String
        
        @param newFileName: name (only) of the new file.
        @type newFileName: String
        
        @param makeNewPath (optional): indicates whether to create the new file path if necessary
        @type makeNewPath: Boolean
        
        @return Boolean
        """
        if self.copy(pathToSourceFile, sourceFileName, pathToNewFile, newFileName, makeNewPath):
            if self.deleteFile(pathToSourceFile, sourceFileName):
                return True
            else:
                return False 
        else:
            return False
        
    def makeDirectory(self, newDirectory):
        """
        Uses os.makedirs to create a new directory at specified location
        
        @param newDirectory: path to create
        @type newDirectory: String
        
        @return Boolean
        """
        if self.directoryExists(newDirectory):
            self._errMsg = "The directory '{newDirectory}' already exists. No need to create it.".format(newDirectory=newDirectory) 
            return True
        else:
            try:
                os.makedirs(newDirectory)
                self._outMsg = "New directory '{newDirectory}' was created successfully.".format(newDirectory=newDirectory) 
            except OSError as oerr:
                self._errMsg = "New directory '{newDirectory}' could not be created! OSError={oerr}".format(newDirectory=newDirectory, oerr=oerr) 
                return False
        
        return True
    
    def renameFile(self, pathToSourceFile, fileToRename, newFileName, keepOriginal=False):
        """
        Uses shutil module to rename a file.
        
        @param pathToSourceFile: path (only) of file to rename.
        @type pathToSourceFile: String
        
        @param fileToRename: name (only) of source file to rename.
        @type fileToRename: String
        
        @param newFileName: name of new file to create
        @type newFileName: String
        
        @param keepOriginal (optional): indicates whether to remove the original file or keep it around
        @type keepyOriginal: Boolean
        
        @return Boolean
        """
        if self.copy(pathToSourceFile, fileToRename, pathToSourceFile, newFileName):
            if keepOriginal:
                self.deleteFile(pathToSourceFile, fileToRename)
        else:
            return False
        
        return True
    
    def deleteFile(self, pathToSourceFile, fileToDelete):
        """
        Uses os.remove to delete file.
        
        @param pathToSourceFile: path (only) of file to remove.
        @type pathToSourceFile: String
        
        @param fileToDelete: name (only) of file to remove.
        @type fileToDelete: String
        
        @return False
        """
        deletethisfile = os.path.join(pathToSourceFile, fileToDelete)
        if not self.filesExist(deletethisfile):
            self._errMsg = "File '{deletethisfile}' does not exist and thus cannot be deleted!".format(deletethisfile=deletethisfile) 
            return False
        else:
            try:
                os.remove(deletethisfile)
                self._outMsg = "File '{deletethisfile}' was removed.".format(deletethisfile=deletethisfile)
            except OSError as oerr:
                self._errMsg = "There was a problem deleting file '{deletethisfile}'. OSError={oerr}".format(deletethisfile=deletethisfile, oerr=oerr)
                return False
            
        return True