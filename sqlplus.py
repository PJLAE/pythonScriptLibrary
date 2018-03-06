#! /usr/bin/python36
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
#[]  Script: sqlplus.py                                                        []
#[]  Script Language: Python 3.6(.4)                                           []
#[]  Description: This class can be used to run sqlplus program to connect to  []
#[]               an Oracle database an execute commands.                      []
#[]  Author: Paul J. Laue                                                      []
#[]  Created: February 23, 2018 09:24:00 AM                                    []
#[] ========================================================================== []
#[]  CHANGE LOG                                                                []
#[]  ----------                                                                []
#[]                                                                            []
#[] ========================================================================== []
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
import subprocess
import os.path

class SQLPlus:
    """
    This class handles the connection to an Oracle database by executing SQLPlus
    via the subprocess module.  SQL commands can then be executed on the SQLPlus
    connection.
    """
    def __init__(self, programLocation=None, connectionString=None):
        """
        Create a new empty SQLPlus object.
        
        @param programLocation (optional): location of the sub-program to be executed.
        @type programLocation: String
        
        @param connectionString (optional): an oracle database connection string
        @type connectionString: String
        """
        if connectionString is not None:
            self.setConnectionString(connectionString)
        else:
            self._connectionstr = None
            
        if programLocation is not None:
            self.setProgramLocation(programLocation)
        else:
            self._prglocation = None
            
        self._errMsg = ''
        self._outMsg = ''
        self._cmd = None
        self._timeout = None
        self._switches = []
        self._sql = ''
        self._qryresults = []
        
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
            
    def setConnectionString(self, connectionString):
        """
        Set the database connection string in format 'username/password@db'
        
        @param connectionString: a database connection string
        @type connectionString: String
        """
        if connectionString is not None and len(connectionString) > 0:
            self._connectionstr = connectionString
        else:
            if len(connectionString) == 0 and len(self._connectionstr) == 0:
                raise Exception("A connection string is required before calling the 'open' method!")
    
    def addCommandSwitch(self, switch):
        """
        Set the command line switches to be run when invoking the sub-program.
        
        @param args a list of switches to include when invoking sub-program.
        @type List/Sequence
        """
        if switch is not None and len(switch) > 0:
            self._switches.append(switch)
            
    def clearCommandSwitches(self):
        """
        Clears out any command switches currently set.
        """
        if len(self._switches) > 0:
            self._switches.clear()
            
    def getQueryResultRowCount(self):
        """
        Returns the number or rows in the query result list.
        
        @return Integer
        """
        return len(self._qryresults) if not self._qryresults is None else 0
    
    def getQueryResultsAsList(self):
        """
        Returns any query results.
        
        @return List
        """
        return self._qryresults if len(self._qryresults) > 0 else None
    
    def clearQueryResults(self):
        """
        Clears out any query results
        """
        if len(self._qryresults) > 0:
            self._qryresults.clear()
    
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
    
    def setSQL(self, sql):
        """
        Set the SQL to execute.
        
        @param sql: a set of SQL statements to execute
        @type: String
        """
        if sql is None or len(sql) == 0:
            return False
        else:
            self._sql = str.encode(sql)
            
        return True    
            
    def setSQLFromFile(self, file):
        """
        Uses a text file containing SQL to set statements to execute.
        
        @param file: full path to a file containing SQL
        @type file: String
        """
        if self.filesExist(file):
            try:
                with open(file, 'r') as fl:
                    self.setSQL(fl.read())
                return True                    
            except OSError as oerr:
                self._errMsg = "There was a critical error attempting to open file '{0}'.  OSError={1}".format(file, str(oerr))
                return False
        else:
            self._errMsg = "The file '{file}' does not exist or is invalid!".format(file=file)
            return False
        
    def executeSQLPlus(self, connectionString=None, sql=None, sqlFile=None):
        """
        Uses the Subprocess module to execute the SQLPlus program
        
        @param connectionString: an oracle database connection string
        @type connectionString: String
        
        @param sql: a series of SQL statements to run via SQLPlus
        @type sql: String
        
        @param sqlFile: full path to a file containing SQL statements to run via SQLPlus
        @type sqlFile: String
        
        @return Boolean
        """
        if connectionString is not None:
            self.setConnectionString(connectionString)
            
        if sql is not None:
            self.setSQL(sql)
            
        if sqlFile is not None:
            self.setSQLFromFile(sqlFile)
      
        cmdswitches = None
        if len(self._switches) > 0:
            cmdswitches = self._switches
        
        if self._prglocation is not None and cmdswitches is None:
            cmd = [self._prglocation, self._connectionstr]
        elif self._prglocation is not None and cmdswitches is not None:
            cmd = [self._prglocation] + cmdswitches +  [self._connectionstr]
        elif self._prglocation is None and cmdswitches is not None:
            cmd = ['sqlplus'] + cmdswitches + [self._connectionstr]
        else:
            cmd = ['sqlplus', self._connectionstr]
        
        sub = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        try:
            sub.stdin.write(self._sql)
            stdout, stderr = sub.communicate(timeout=self._timeout)
            print("Standard Out: {stdout}".format(stdout=stdout))
            self._qryresults = stdout.decode('utf-8').split("\n")
        except subprocess.TimeoutExpired:
            sub.kill()
            stdout, stderr = sub.communicate()
        finally:
            self._errMsg = stderr
            self._outMsg = stdout
                
        return True