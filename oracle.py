#! /usr/bin/python36
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
#[]  Script: oracle.py                                                         []
#[]  Script Language: Python 3.6(.4)                                           []
#[]  Description: This class can be used to connect to an Oracle database and  []
#[]               execute sql commands by using the cx_Oracle module.          []
#[]  Author: Paul J. Laue                                                      []
#[]  Created: February 23, 2018 4:03:00 PM                                     []
#[] ========================================================================== []
#[]  CHANGE LOG                                                                []
#[]  ----------                                                                []
#[]                                                                            []
#[] ========================================================================== []
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
import cx_Oracle
import os.path
import sys

class OracleDB:
    """
    This class handles the connection to an Oracle database and execution of 
    SQL statement(s) or stored procedures.
    """
    def __init__(self, connectionString=None):
        """
        Create a new empty OracleDB object.
        
        @param connectionString: an oracle database connection string
        @type connectionString: String 
        """
        self._errMsg = ''
        self._outMsg = ''
        
        if connectionString is not None:
            self.setConnectionString(connectionString)
        else:
            self._connectionstr = None
            
        self._sql = ''
        self._connection = None
        self._queryresults = []
        self._transactions = []
        
    def open(self, connectionString=None):
        """
        Attempts to open an database connection using connection string.
        
        @param connectionString: an oracle database connection string
        @type connectionString: String
        
        @return Boolean
        """
        if not connectionString is None:
            self.setConnectionString(connectionString)
            
        try:
            self._connection = cx_Oracle.connect(self._connectionstr)
            self._outMsg = "Oracle database connection opened."
        
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self._errMsg = "[Oracle-Error-Message: " + str(error.message) + "] with [System Error: " + str(sys.stderr) + "]"
            return False
        
        return True
    
    def close(self):
        """
        Attempts to close the database connection if it is open.
        """
        if not self._connection is None:
            self._connection.close()
            
    def begin(self):
        """
        Attempts to start a transaction on the current connection.
        """
        if not self._connection is None:
            self._connection.begin()
            
    def commit(self):
        """
        Attempts to commit a transaction on the current connection.
        """
        if not self._connection is None:
            self._connection.commit()
            
    def rollback(self):
        """
        Attempts to rollback a transaction on the current connection.
        """
        if not self._connection is None:
            self._connection.rollback()
        
    def runStoredProcedure(self, storedProcedureName, params=[]):
        """
        Use existing database connection to execute a stored procedure.
        
        @param storedProcedureName: name of stored procedure
        @type storedProcedureName: String
        
        @param params: a list of parameters to be used when calling stored procedure
        @type params: List
        
        @return Boolean
        """
        if self._connection is None:
            db = self.open(self.setConnectionString(self._connectionstr))
        else:
            db = self._connection
        
        try:    
            cursor = db.cursor()
            if len(params) > 0:
                cursor.callproc(storedProcedureName, params)
            else:
                cursor.callproc(storedProcedureName)
                
            return True
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self._errMsg = "[Oracle-Error-Message: " + str(error.message) + "] with [System Error: " + str(sys.stderr) + "]"
            return False
        finally:
            cursor.close()
    
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
               
    def getQueryResultRowCount(self):
        """
        Returns the number or rows in the query result list.
        
        @return Integer
        """
        return len(self._queryresults) if not self._queryresults is None else 0
    
    def getQueryResultsAsList(self):
        """
        Returns any query results.
        
        @return List
        """
        return self._queryresults if len(self._queryresults) > 0 else None
    
    def clearQueryResults(self):
        """
        Clears out any query results
        """
        if len(self._queryresults) > 0:
            self._queryresults.clear()
            
    def getAllTransactionsInQueue(self):
        """
        Returns all the transactions in the queue.
        
        @return List of all transactions in queue.
        """
        if not self._transactions is None:
            return self._transactions
        
    def removeTransactionFromQueue(self, itemIndex):
        """
        Attempts to remove a transaction from the queue.
        
        @param itemIndex: item index of the row to remove.  NOTE:  Zero based index.
        @type itemIndex: Integer
        
        @return Boolean
        """
        if type(itemIndex) != int: return False
        
        try:
            if not self._transactions is None:
                self._transactions.remove(itemIndex)
                
            return True
        except ValueError as verr:
            self._errMsg = "No item at index {itemIndex} could be found! Error: {verr}".format(itemIndex=itemIndex, verr=verr)
            return False
            
    def addTransactionToQueue(self, transaction):
        """
        Adds a new transaction to the transaction list.
        
        @param transaction: a transaction statement to add to the queue.
        @type transaction: String
        """
        if not self._transactions is None:
            self._transactions.append(transaction)
            
    def getTransactionFromQueue(self, itemIndex=None):
        """
        Attempts to retrieve a transaction from the queue.
        
        @param itemIndex (optional): item index of the row to remove.  NOTE:  Zero based index.
        @type itemIndex: Integer
        
        @return String
        """
        if not self._transactions is None:
            if itemIndex is None:
                return str(self._transactions.pop())
            else:
                return str(self._transactions.pop(itemIndex))
        else:
            return ''
            
    def getTransactionCount(self):
        """
        Returns the count of transactions in the queue.
        """
        return len(self._transactions) if not self._transactions is None else 0
            
    def clearAllTransactionsFromQueue(self):
        """
        Clears out the transaction queue.
        """
        if not self._transactions is None:
            self._transactions.clear()
    
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
        if not sql is None and len(sql) > 0:
            self._sql = str.encode(sql)
            
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
        
    def executeCommand(self, connectionString=None, sql=None, sqlFile=None):
        """
        Runs sql command/statement and stores results in a list array.  Uses connection string and 
        sql if passed in as arguments.
        
        @param connectionString (optional): an oracle database connection string
        @type connectionString: String
        
        @param sql (optional): a series of SQL statements to run via SQLPlus
        @type sql: String
        
        @param sqlFile (optional): full path to a file containing SQL statements to run via SQLPlus
        @type sqlFile: String
        
        @return Boolean
        """
        if connectionString is not None:
            self.setConnectionString(connectionString)
            
        if sql is not None:
            self.setSQL(sql)
            
        if sqlFile is not None:
            self.setSQLFromFile(sqlFile)
            
        try:
            if self._connection is None:
                self.open(self._connectionstr)
                
            sqlcursor = self._connection.cursor()
            sqlcursor.execute(self._sql)
            results = sqlcursor.fetchall()
            rowcount = len(results)
            if rowcount > 0:
                self._outMsg = "Query returned {rowcount} rows".format(rowcount=rowcount)
                self._queryresults = results;
            else:
                self._outMsg = "Query return 0 rows."
                
            return True
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self._errormsg = "[Oracle-Error-Message: " + str(error.message) + "] with [System Error: " + str(sys.stderr) + "]"
            return False
        finally:
            sqlcursor.close()
            
    def executeBasicTransaction(self, connectionString=None, transaction=None, transFile=None):
        """
        Attempts to perform a basic (simple) transaction.  Uses connection string and sql if passed
        in as arguments.
        
        @param connectionString (optional): an oracle database connection string
        @type connectionString: String
        
        @param transaction (optional): a series of SQL statements to run via SQLPlus
        @type transaction: String
        
        @param transFile (optional): full path to a file containing SQL statements to run via SQLPlus
        @type transFile: String
        
        @return Boolean
        """
        if connectionString is not None:
            self.setConnectionString(connectionString)
            
        if transaction is not None:
            self.setSQL(transaction)
            
        if transFile is not None:
            self.setSQLFromFile(transFile)
            
        try:
            if self._connection is None:
                self.open(self._connectionstr)
                
            self.begin()
            
            sqlcursor = self._connection.cursor()
            sqlcursor.execute(self._sql)
            results = sqlcursor.fetchall()
            rowcount = len(results)
            if rowcount > 0:
                self._outMsg = "Query returned {rowcount} rows".format(rowcount=rowcount)
                self._queryresults = results;
            else:
                self._outMsg = "Query return 0 rows."
                
            self.commit()    
                
            return True
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self._errormsg = "[Oracle-Error-Message: " + str(error.message) + "] with [System Error: " + str(sys.stderr) + "]"
            self.rollback()
            return False
        finally:
            sqlcursor.close()
            
    def executeMultiTransaction(self, transactionFirst, transactionSecond, connectionString=None):
        """
        Attempts to perform an advanced transaction using 2 sql (transaction) statements. Uses connection string
        if passed in as argument.
        
        @param transactionFirst: first transaction to perform in scope
        @type transactionFirst: String
        
        @param transactionSecond: second transaction to perform in scope
        @type transactionSecond: String
        
        @param connectionString (optional): an oracle database connection string
        @type connectionString: String
        
        @return Boolean
        """
        if connectionString is not None:
            self.setConnectionString(connectionString)
            
        try:
            if self._connection is None:
                self.open(self._connectionstr)
                
            self.begin()
            
            trans1 = self._connection.cursor()
            trans1.execute(transactionFirst)
            
            trans2 = self._connection.cursor()
            trans2.execute(transactionSecond)
            
            self.commit()
            
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self._errormsg = "[Oracle-Error-Message: " + str(error.message) + "] with [System Error: " + str(sys.stderr) + "]"
            self.rollback()
            return False
        finally:
            trans1.close()
            trans2.close()
            
    def executeAdvancedTransaction(self, connectionString=None):
        """
        Attempts to perform an advanced transaction using many sql transaction statements.  Uses connection string
        if passed in as an argument.
        
        @param connectionString (optional): an oracle database connection string
        @type connectionString: String
        
        @return Boolean
        """
        if connectionString is not None:
            self.setConnectionString(connectionString)
            
        if self.getTransactionCount() == 0:
            self._errMsg = "Advanced transaction must have at least 1 transaction."
            return False
        
        try:
            self.begin()
            trancursors = []
            for tran in self.getAllTransactionsInQueue():
                tc = self._connection.cursor()
                tc.execute(tran)
                trancursors.append(tc)
            
            self.commit()
                
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self._errormsg = "[Oracle-Error-Message: " + str(error.message) + "] with [System Error: " + str(sys.stderr) + "]"
            self.rollback()
            return False
        finally:
            for curs in trancursors:
                curs.close()