#! /usr/bin/python36
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
#[]  Script: compressor.py                                                     []
#[]  Script Language: Python 3.6(.4)                                           []
#[]  Description: This class can be used to compress/uncompress a file using   []
#[]               zipfile and zlib modules.  This class also allows for the    []
#[]               use of 7zip as a subprocess.                                 []
#[]  Author: Paul J. Laue                                                      []
#[]  Created: February 20, 2018 09:24:00 AM                                    []
#[] ========================================================================== []
#[]  CHANGE LOG                                                                []
#[]  ----------                                                                []
#[]                                                                            []
#[] ========================================================================== []
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
import subprocess
import zipfile
import tarfile
import os.path
import re


class Compressor:
    """
    This class handles compression/decompression and extraction of archive files as well 
    as allows for the use of a secondary program called 7zip which is executed via the 
    subprocess module.
    """
    def __init__(self, programLocation=None):
        """
        Creates a new empty Compressor object.
        
        @param programLocation: location of the sub-program to be executed.
        @type programLocation: String
        """
        self._cmd = None
        self._errMsg = ''
        self._outMsg = ''
        self._timeout = None
        if programLocation is not None:
            self._prglocation = programLocation if self.installIsValid(programLocation) else None
        else:
            self._prglocation = None
            
        self._args = []
        self._comprlevel = 0
    
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
    
    def setTimeOut(self, timeout):
        """
        Sets the timeout that will be used when calling any sub-program.
        
        @param timeout: a timeout value to use when calling sub-program.
        @type timeout: Integer
        """
        if timeout is None:
            self._timeout = None
        elif timeout is not None and len(timeout) > 0 and type(timeout) == int: 
            self._timeout = timeout
        
    def addCommandArg(self, arg):
        """
        Set the command line arguments to be run when invoking the sub-program.
        
        @param args a list of arguments to include when invoking sub-program.
        @type List/Sequence
        """
        if arg is not None and len(arg) > 0:
            self._args.append(arg)
        
    def clearCommandArgs(self):
        """
        Clears out any command arguments currently set.
        """
        if len(self._args) > 0:
            self._args.clear()
        
    def setProgramLocation(self, programLocation):
        """
        Set the program location of the sub-program to run.
        
        @param programLocation: a valid path to the program to run.
        @type programLocation: String
        """
        if self.installIsValid(programLocation):
            self._prglocation = programLocation
        
    def installIsValid(self, installLocation=None):
        """
        Attempts to validate that the 7Zip program exists at its given location.
        
        @param installLocation: a local path for the installed program.
        @type installLocation: String
        
        @return Boolean
        """
        if installLocation is None:
            if self._prglocation is None: return False
            else:
                if not os.path.isfile(self._prglocation): return False                
            return True
        else:
            if os.path.isfile(installLocation): return True
            elif os.path.exists(installLocation): return True
            else: return False
    
    def createArchiveAsZip(self, archive, filesToInclude, compressionLevel=0):
        """
        Attempts to use the zipfile module to create a new archive.
        
        @param archive: filename and path to new archive file.
        @type archive: String
        
        @param filesToInclude: a list of files to include in the new archive.
        @type filesToInclude: List/Sequence
        
        @param compressionLevel (optional): the level of compression to be used. (0=ZIP_STORED, 8=ZIP_DEFLATED, 12=ZIP_BZIP2, 14=ZIP_LZMA)
        @type compressionLevel: Integer (numeric constant as defined by zipfile)
        
        @return Boolean
        """
        if archive is None:
            self._errMsg = "The parameter '{archive}' is missing or invalid!".format(archive=archive)
            return False
        elif not self.filesExist(filesToInclude):
            self._errMsg = "One or more files are missing or invalid!"
            return False
        else:            
            if compressionLevel is not None:
                # validate compression level
                if not compressionLevel == 0 and not compressionLevel == 8 and not compressionLevel == 12 and not compressionLevel == 14:
                    self.setCompressionLevel(0)
                else:
                    self.setCompressionLevel(compressionLevel)
            
            if self._comprlevel == 8:
                cmprss = zipfile.ZIP_DEFLATED
            elif self._comprlevel == 12:
                cmprss = zipfile.ZIP_BZIP2
            elif self._comprlevel == 14:
                cmprss = zipfile.ZIP_LZMA
            else:
                cmprss = zipfile.ZIP_STORED
            
            try:
                zf = zipfile.ZipFile(archive, mode='x')
                for f in filesToInclude:
                    zf.write(f, compress_type=cmprss)
                    
                self._outMsg = "Zip archive '{archive}' created successfully!".format(archive=archive)
            except zipfile.BadZipFile as berr:
                self._errMsg = "There was an error attempting to open zip file '{0}' and add to it.  BadZipFile={1}".format(archive, str(berr))
                return False
            except OSError as oerr:
                self._errMsg = "There was a critical error attempting to open zip file '{0}' and add to it.  OSError={1}".format(archive, str(oerr))
                return False
            finally:
                zf.close()
            
            return True
    
    def extractZipArchive(self, archive, pathToFiles, password=None):
        """
        Attempt to extract a zip archive.
        
        @param archive:  filename and path to archive file containing files to extract.
        @type archive: String
        
        @param pathToFiles: location of where files should be extracted to.
        @type pathToFiles: String
        
        @return Boolean
        """
        if archive is None:
            self._errMsg = "The parameter '{archive}' is missing or invalid!".format(archive=archive)
            return False
        elif not zipfile.is_zipfile(archive):
            self._errMsg = "File '{archive}' is not a valid zip file!".format(archive=archive)
            return False
        else:
            extracttocurrentdir = False
            # is the path to extract files to valid?
            if not self.directoryExists(pathToFiles):
                try:
                    os.makedirs(pathToFiles)
                    self._outMsg = "Files extracted to '{pathToFiles}' or current working directory if path cannot be determined.".format(pathToFiles=pathToFiles)
                except OSError:
                    self._errMsg = "Cannot extract files to specified location '{pathToFiles}'. Will extract to current directory instead.".format(pathToFiles=pathToFiles)
                    extracttocurrentdir = True
            else:
                self._outMsg = "Files extracted to '{pathToFiles}'.".format(pathToFiles=pathToFiles)
            
            if password is not None:
                password = str.encode(password)
                
            try:
                with zipfile.ZipFile(archive, mode='r') as zf:
                    zf.extractall(pwd=password) if extracttocurrentdir else zf.extractall(path=pathToFiles, pwd=password)
                    
                self._outMsg = "Files extracted to '{pathToFiles}'.".format(pathToFiles=pathToFiles)
            except zipfile.BadZipFile as berr:
                self._errMsg = "There was an error attempting to open zip file '{0}' and add to it.  BadZipFile={1}".format(archive, str(berr))
                return False
            except OSError as oerr:
                self._errMsg = "There was a critical error attempting to open zip file '{0}' and add to it.  OSError={1}".format(archive, str(oerr))
                return False
            
            return True        
                            
    def createArchiveWith7Zip(self, archive, filesToInclude):
        """
        Attempts to call the 7Zip program as a subprocess to produce an archive using arguments populated via the addCommandArg method.
        
        @param archive: filename and path to new archive file.
        @type archive: String
        
        @param filesToInclude: a list of files to include in the new archive.
        @type filesToInclude: List/Sequence
        
        @return Boolean
        """
        if archive is None:
            self._errMsg = "The parameter '{archive}' is missing or invalid!".format(archive=archive)
            return False
        elif not self.filesExist(filesToInclude):
            self._errMsg = "One or more files are missing or invalid!"
            return False
        else:
            if len(self._args) > 0:
                cmdargs = self._args
                cmd = [self._prglocation, 'a'] + cmdargs + [archive] + filesToInclude                
            else:
                cmd = [self._prglocation, 'a', archive] + filesToInclude
                            
            sub = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
            try:
                outs, err = sub.communicate(timeout=self._timeout)
            except subprocess.TimeoutExpired:
                sub.kill()
                outs, err = sub.communicate()
            finally:
                self._errMsg = err
                self._outMsg = outs
                
            return True
    
    def extract7ZipArchive(self, archive):
        """
        Attempts to call 7Zip program as a subprocess to extract an archive using arguments populated via the addCommandArgs method.
        
        @param archive: filename and path to archive file.
        @type archive: String
        
        @return Boolean
        """        
        if archive is None:
            self._errMsg = "The parameter '{archive}' is missing or invalid!".format(archive=archive)
            return False
        else:
            if self.isZipFile(archive):
                if len(self._args) > 0:
                    cmdargs = self._args
                    cmd = [self._prglocation, 'e'] + [archive] + cmdargs
                else:
                    cmd = [self._prglocation, 'e'] + [archive]
            
                sub = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
             
                try:
                    outs, err = sub.communicate(timeout=self._timeout)
                except subprocess.TimeoutExpired:
                    sub.kill()
                    outs, err = sub.communicate()
                finally:
                    self._errMsg = err
                    self._outMsg = outs
                
                return True
            else:
                self._errMsg = "File '{archive}' is not a valid zip file!".format(archive=archive)
                return False
    
    def createArchiveWithGZip(self, archive, filesToInclude, compressionLevel=0):
        """
        Uses tarfile module to produce a gzip archive with the ability to set the level of compression.
        
        @param archive: filename and path to new archive file.
        @type archive: String
        
        @param filesToInclude: a list of files to include in the new archive.
        @type filesToInclude: List/Sequence
        
        @param compressionLevel (optional): the level of compression to be used. (0=None, 9=Maximum)
        @type compressionLevel: Integer
        
        @return Boolean
        """
        if archive is None:
            self._errMsg = "The parameter '{archive}' is missing or invalid!".format(archive=archive)
            return False
        elif not self.filesExist(filesToInclude):
            self._errMsg = "One or more files are missing or invalid!"
            return False
        else:
            if compressionLevel is not None:
                self.setCompressionLevel(compressionLevel)
            
            try:
                with tarfile.open(archive, "x:gz", compresslevel=self._comprlevel) as newarch:            
                    for file in filesToInclude: newarch.add(file)
                
                self._outMsg = "GZip archive '{archive}' created successfully!".format(archive=archive)
            except tarfile.TarError as terr:
                self._errMsg = "There was an error attempting to open tar file '{0}' and add to it.  TarError={1}".format(archive, str(terr))
                return False
            except OSError as oerr:
                self._errMsg = "There was a critical error attempting to open tar file '{0}' and add to it.  OSError={1}".format(archive, str(oerr))
                return False
            
            return True
    
    def createArchiveWithBZip2(self, archive, filesToInclude, compressionLevel=0):
        """
        Uses tarfile module to produce a bzip2 archive with the ability to set the level of compression.
        @param archive: filename and path to new archive file.
        @type archive: String
        
        @param filesToInclude: a list of files to include in the new archive.
        @type filesToInclude: List/Sequence
        
        @param compressionLevel (optional): the level of compression to be used. (0=None, 9=Maximum)
        @type compressionLevel: Integer
        
        @return Boolean
        """
        if archive is None:
            self._errMsg = "The parameter '{archive}' is missing or invalid!".format(archive=archive)
            return False
        elif not self.filesExist(filesToInclude):
            self._errMsg = "One or more files are missing or invalid!"
            return False
        else:
            if compressionLevel is not None:
                self.setCompressionLevel(compressionLevel)
                
            try:
                with tarfile.open(archive, "x:bz2", compresslevel=self._comprlevel) as newarch:            
                    for file in filesToInclude: newarch.add(file)
                    
                self._outMsg = "BZip2 archive '{archive}' created successfully!".format(archive=archive)
            except tarfile.TarError as terr:
                self._errMsg = "Error attempting to open tar file '{0}' and add to it.  TarError={1}".format(archive, str(terr))
                return False
            except OSError as oerr:
                self._errMsg = "Critical error attempting to open tar file '{0}' and add to it.  OSError={1}".format(archive, str(oerr))
                return False
            
            return True
    
    def extractTarArchive(self, archive, pathToFiles):
        """
        Attempt to extract a tar archive.
        
        @param archive:  filename and path to archive file containing files to extract.
        @type archive: String
        
        @param pathToFiles: location of where files should be extracted to.
        @type pathToFiles: String
        
        @return Boolean
        """
        if archive is None:
            self._errMsg = "The parameter '{archive}' is missing or invalid!".format(archive=archive)
            return False
        else:
            if self.isTarFile(archive):
                extracttocurrentdir = False
                # is the path to extract files to valid?
                if not self.directoryExists(pathToFiles):
                    try:
                        os.makedirs(pathToFiles)
                        self._outMsg = "Files extracted to '{pathToFiles}' or current working directory if path cannot be determined.".format(pathToFiles=pathToFiles)
                    except OSError:
                        self._errMsg = "Cannot extract files to specified location '{pathToFiles}'. Will extract to current directory instead.".format(pathToFiles=pathToFiles)
                        extracttocurrentdir = True
                else:
                    self._outMsg = "Files extracted to '{pathToFiles}'.".format(pathToFiles=pathToFiles)
                
                try:                    
                    # is this a gzip file?
                    if re.search(".gz", archive) is not None:
                        with tarfile.open(archive, "r:gz") as gzfile:
                            gzfile.extractall() if extracttocurrentdir else gzfile.extractall(path=pathToFiles)
                    elif re.search(".bz2", archive) is not None:
                        with tarfile.open(archive, "r:bz2") as bzfile:
                            bzfile.extractall() if extracttocurrentdir else bzfile.extractall(path=pathToFiles) 
                    else:
                        self._errMsg = "Archive type could not be determined!"
                        return False

                except tarfile.TarError as terr:
                    self._errMsg = "Error attempting to extract files from tar file '{0}'. TarError={1}".format(archive, str(terr))
                    return False
                except OSError as oerr:                     
                    self._errMsg = "Critical error attempting to extract files from tar file '{0}'. OSError={1}".format(archive, str(oerr))
                    return False
                
                return True
                
            else:
                self._errMsg = "File '{archive}' is not a valid tar file!".format(archive=archive)
                return False
    
    def get7ZipFileMembers(self, archive, password=None):
        """
        Attempts to retrieve file (member) info from a zipped archive.
        
        @param archive: filename and path to archive file containing files to extract.
        @type archive: String
        """
        if archive is None:
            self._errMsg = "The parameter '{archive}' is missing or invalid!".format(archive=archive)
            return None
        else:
            if password is not None:
                with zipfile.ZipFile.open(archive,'r', pwd=password) as zf:
                    return zf.namelist()
            else:
                with zipfile.ZipFile.open(archive,'r') as zf:
                    return zf.namelist()
    
    def getTarFileMembers(self, archive):
        """
        Attempts to retrieve file (member) info from a tar'd archive.
        
        @param archive: filename and path to archive file containing files to extract.
        @type archive: String
        
        @return: List
        """
        if archive is None:
            self._errMsg = "The parameter '{archive}' is missing or invalid!".format(archive=archive)
            return None
        else:
            try:
                if self.isTarFile(archive):
                    return tarfile.open(archive, 'r:*').getmembers()
                else:
                    return None
            except tarfile.TarError as terr:
                self._errMsg = "Error attempting to extract files from tar file '{0}'. TarError={1}".format(archive, str(terr))
                return None
            except OSError as oerr:                     
                self._errMsg = "Critical error attempting to extract files from tar file '{0}'. OSError={1}".format(archive, str(oerr))
                return None
    
    def isTarFile(self, file):
        """
        Attempts to determine if the file is a valid tar file.
        
        @param file: path and filename of the file in question.
        @type file: String
        
        @return Boolean
        """
        return (os.path.isfile(file) and tarfile.is_tarfile(file))
    
    def isZipFile(self, file):
        """
        Attempts to determine if the file is a valid zip file.
        
        @param file: path and filename of the file in question.
        @type file: String
        
        @return Boolean
        """
        return (os.path.isfile(file) and zipfile.is_zipfile(file))
            
    def setCompressionLevel(self, compressionLevel):
        """
        Set the compression level to be used when creating a compressed archive.
        
        @param compressionLevel: the level of compression to be used.
        @type compressionLevel: Integer
        """
        if type(compressionLevel) == int:
            self._comprlevel = compressionLevel
        
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