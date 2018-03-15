#! /usr/bin/python36
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
#[]  Script: ad.py                                                             []
#[]  Script Language: Python 3.6(.4)                                           []
#[]  Description: This class uses the ldap3 module to access Active Directory  []
#[]               information.                                                 []
#[]  Author: Paul J. Laue                                                      []
#[]  Created: March 6, 2018 03:24:00 PM                                        []
#[] ========================================================================== []
#[]  CHANGE LOG                                                                []
#[]  ----------                                                                []
#[]                                                                            []
#[] ========================================================================== []
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
import os.path
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, AUTO_BIND_NO_TLS, SUBTREE
from ldap3.core.exceptions import LDAPCursorError
from ldap3.core.tls import Tls
import ssl
from test.test_binop import isnum
from enum import Enum
import re
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        
        return json.JSONEncoder.default(self, o)

class AttributeSet(Enum):
    BASIC=1,
    COMPREHENSIVE=2,
    ALL=3

class FilterBy(Enum):
    NONE=1,
    EMPLID=2,
    LOGINID=3,
    LASTNAME=4,
    FIRSTNAME=5,
    DISPLAYNAME=6,
    EMAIL=7,
    EMPSTATUS=8,
    DEPTID=9,
    JOBTITLE=10

class AccountType(Enum):
    EMPLOYEE=1,
    DISABLED=2,
    PRIVILEGED=3,
    SHARED=4,
    SERVICE=5,
    TEST=6,
    VENDOR=7

class ActiveDirectory:
    """
    This class uses the ldap3 module to establish a connection to Active Directory and retrieve directory information.
    """
        
    def __init__(self, serverName=None, domainName=None, userName=None, userPassword=None):
        """
        Creates a new empty ActiveDirectory object.
        
        @param serverName (optional): name of the ldap server
        @type serverName: String
        
        @param domainName (optional): name of the domain to connect to
        @type domainName: String
        
        @param userName (optional): name of the connecting user
        @type userName: String
        
        @param userPwd (optional): password for the connecting user
        @type userPwd: String
        """
        self._servername = serverName
        self._domainname = domainName
        self._username = userName
        self._userpwd = userPassword
        self._port = None
        self._usessl = True
        self._usetls = False
        self._privatekeyfile = None
        self._servercertificate = None
        self._cacertificates = None
        self._errMsg = ''
        self._outMsg = ''
        self._forcesvrcertvalidation = False
        self._conn = None
        
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

    def setClientCertificate(self, certificateFile):
        """
        Sets the client certificate file.  This is the private key for the x509 server certificate attempting to connect to the LDAP server.
        
        @param certificateFile: a certificate file used by the client (USAGE: path + filename)
        @type certificateFile: String
        
        @return Boolean
        """
        if self.filesExist(certificateFile):
            self._privatekeyfile = certificateFile
            return True
        else:
            self._outMsg = "Client certificate '{certificateFile}' does not exist!".format(certificateFile=certificateFile)
            return False
        
    def setServerCertificate(self, certificateFile):
        """
        Sets the server certificate file.  This is an X509 certificate for the server attempting to connect to the LDAP server.
        
        @param certificateFile: a certificate file used by the server (USAGE: path + filename)
        @type certificateFile: String
        
        @return Boolean
        """
        if self.filesExist(certificateFile):
            self._servercertificate = certificateFile
            return True
        else:
            self._outMsg = "Server certificate '{certificateFile}' does not exist!".format(certificateFile=certificateFile)
            return False
        
    def setCACertificate(self, certificateFile):
        """
        Sets the CA certificate file.  This is the CA for the LDAP server certificate
        
        @param certificateFile: a certificate file used by the client (USAGE: path + filename)
        @type certificateFile: String
        
        @return Boolean
        """
        if self.filesExist(certificateFile):
            self._cacertificates = certificateFile
            return True
        else:
            self._outMsg = "CA certificate '{certificateFile}' does not exist!".format(certificateFile=certificateFile)
            return False
        
    def setForceServerCertificateValidation(self, force=False):
        """
        Sets whether server certificate should be validated or not.
        
        @param force: indicates if server certificate validation should occur during connection.
        @type force: Boolean
        """
        self._forcesvrcertvalidation = force
        
    def hasValidConnectionInformation(self):
        """
        Returns True if all relevant connection information is available, otherwise False
        
        @return Boolean
        """
        if self._servername is not None and self._domainname is not None and self._username is not None and self._userpwd is not None:
            # Check to see if SSL is enabled and if certificates are accounted for
            if self._usessl and self._forcesvrcertvalidation:
                if self._privatekeyfile is not None and self._servercertificate is not None and self._cacertificates is not None:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False
        
    def getServerName(self):
        """
        Returns the name of the server
        """
        return self._servername
    
    def setPortNumber(self, portNumber):
        """
        Sets the port number to use with the connection.
        """
        if isnum(portNumber):
            self._port = portNumber
    
    def getDomainName(self):
        """
        Returns the name of the domain
        """
        return self._domainname
    
    def useSSLConnection(self, sslEnabled=False):
        """
        Sets whether the connection should use SSL
        
        @param sslEnabled: should the connection use SSL
        @type sslEnabled: Boolean 
        """
        self._usessl = sslEnabled
        
    def useTLSConnection(self, tlsEnabled=False):
        """
        Sets whether the connection should use tls
        
        @param tlsEnabled: should the connection use TLS
        @type tlsEnabled = Boolean
        """
        self._usetls = tlsEnabled
        
    def setConnectionPort(self, port=389):
        """
        Sets the connection port to use.
        
        @param port: the port number to use in the connection
        @type port: Integer
        """
        self._port = port
        
    def getConnectionPort(self):
        """
        Returns the port number to use in the connection
        
        @return Integer
        """
        if self._usessl and self._port is None:
            self.setConnectionPort(636)
        elif not self._usessl and self._port is None:
            self.setConnectionPort(389)

        return self._port
        
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
    
    def getLdapADConnection(self, serverName=None, domainName=None, userName=None, userPassword=None, useSSL=True):
        """
        Returns a connection to Active Directory using the supplied arguments.
        
        @param serverName (optional): name of the ldap server
        @type serverName: String
        
        @param domainName (optional): name of the domain to connect to
        @type domainName: String
        
        @param userName: name of the connecting user
        @type userName: String
        
        @param userPwd: password for the connecting user
        @type userPwd: String
        
        @return Object as type Connection
        """
        if serverName is not None:
            self._servername = serverName
            
        if domainName is not None:
            self._domainname = domainName
            
        if userName is not None:
            self._username = userName
            
        if userPassword is not None:
            self._userpwd = userPassword
            
        self._usessl = useSSL
        
        if self.hasValidConnectionInformation():
            svr = self.ldapServer()
            if svr is not None:
                uname = self._username
                domain = self.getDomainName()
                upwd = self._userpwd
                return Connection(svr, user="{domain}\\{uname}".format(domain=domain, uname=uname), password=upwd, authentication=NTLM, auto_bind=True)        
        else:
            self._errMsg = "The connection does not have enough information to proceed as currently configured!"
            return None
    
    def ldapServer(self):
        """
        Returns an instance of an LDAP server
        
        @return Object of type Server
        """
        if self._servername:
            if self._usetls:
                return Server(self.getServerName(), port=self.getConnectionPort(), use_ssl=self._usessl, tls=self.tlsConfiguration())
            else:
                return Server(self.getServerName(), port=self.getConnectionPort(), use_ssl=self._usessl)
        else:
            self._errMsg = "LDAP server name IS NOT set!"
            return None
        
    def tlsConfiguration(self):
        """
        Returns a TLS configuration object.
        
        @return Object of type Tls
        """
        if self._usetls:
            # if using TLS then we will also be using SSL so set that to True
            self._usessl = True
            
            if self._privatekeyfile is not None and self._servercertificate is not None and self._cacertificates is not None:
                return Tls(local_private_key_file=self._privatekeyfile, local_certificate_file=self._servercertificate, validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file=self._cacertificates)
            else:
                return Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1)
        else:
            print("here")
            return Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_SSLv3)
        
    def getBasicUserAttributes(self):
        """
        Supplies a basic set of attributes to be returned in search.
        
        @return List
        """
        return ['cn', 
                'employeeID', 
                'displayName', 
                'mail', 
                'aliEmployeeStatus']
    
    def getExtensiveUserAttributes(self):
        """
        Supplies a more comprehensive set of attributes to be returned in search.
        
        @return List
        """
        return ['cn', 
                'objectCategory',
                'distinguishedName',
                'objectGUID',
                'sAMAccountName',
                'userPrincipalName',
                'sn',
                'givenName',
                'initials',
                'l',                
                'st',
                'postalCode',
                'employeeID', 
                'displayName', 
                'mail', 
                'aliEmployeeStatus',
                'title',
                'department',
                'physicalDeliveryOfficeName',
                'telephoneNumber',
                'lastLogon',
                'lastLogoff',
                'pwdLastSet',
                'accountExpires']
    
    def getBasicGroupAttributes(self):
        """
        Supplies a basic set of attributes to be returned in search.
        
        @return List
        """
        return ['cn',
                'description',
                'info',
                'name',
                'sAMAccountName',
                'managedBy',
                'whenCreated',
                'whenChanged']
        
    def getExtensiveGroupAttributes(self):
        """
        Supplies a more comprehensive set of attributes to be returned in search.
        
        @return List
        """
        return ['cn',
                'objectCategory',
                'description',
                'distinguishedName',
                'objectGUID',
                'info',
                'name',
                'sAMAccountName',
                'managedBy',
                'whenCreated',
                'whenChanged']
                
    def getBaseDNForGroups(self):
        """
        Returns the base dn to search for groups.
        
        @return String
        """
        return "OU=Groups,DC=ALI,DC=PRI"
        
    def getBaseDNForUsers(self):
        """
        Returns the base dn to search for users.
        
        @return String 
        """
        return "OU=Accounts,DC=ALI,DC=PRI"
    
    def getDN(self, userName, accountType=AccountType.EMPLOYEE):
        """
        Returns a DN query for a specific user
        
        @param userName: the user name for the query
        @type userName: String
        
        @param accountType: the type of account
        @type accountType: Enumeration
        
        @return String
        """
        if accountType == AccountType.VENDOR:
            return "CN={userName},OU=Vendor,OU=Accounts,DC=ALI,DC=PRI".format(userName=userName)
        elif accountType == AccountType.SHARED:
            return "CN={userName},OU=Shared,OU=Accounts,DC=ALI,DC=PRI".format(userName=userName)
        elif accountType == AccountType.SERVICE:
            return "CN={userName},OU=Service,OU=Accounts,DC=ALI,DC=PRI".format(userName=userName)
        elif accountType == AccountType.DISABLED:
            return "CN={userName},OU=Disabled,OU=Accounts,DC=ALI,DC=PRI".format(userName=userName)
        elif accountType == AccountType.TEST:
            return "CN={userName},OU=Test,OU=Accounts,DC=ALI,DC=PRI".format(userName=userName)
        elif accountType == AccountType.PRIVILEGED:
            return "CN={userName},OU=Privileged,OU=Accounts,DC=ALI,DC=PRI".format(userName=userName)
        else:
            return "CN={userName},OU=Internal,OU=Accounts,DC=ALI,DC=PRI".format(userName=userName)
        
    def getFormattedUserSearchFilter(self, filterCriteria, useNegate=False, filterBy=FilterBy.LOGINID):
        """
        Returns a formatted string ready to be used as 
        
        @param filterCriteria: the type of filter to apply to search
        @type Enumerator
        """
        if filterBy == FilterBy.DEPTID:
            if useNegate:
                return "(!(aliDepartmentCode={filterCriteria}))".format(filterCriteria=filterCriteria)
            else:
                return "(aliDepartmentCode={filterCriteria})".format(filterCriteria=filterCriteria)
        elif filterBy == FilterBy.DISPLAYNAME:
            if useNegate:
                return "(!(displayName={filterCriteria}*))".format(filterCriteria=filterCriteria)
            else:
                return "(displayName={filterCriteria}*)".format(filterCriteria=filterCriteria)
        elif filterBy == FilterBy.EMAIL:
            if useNegate:
                return "(!(mail={filterCriteria}*))".format(filterCriteria=filterCriteria)
            else:
                return "(mail={filterCriteria}*)".format(filterCriteria=filterCriteria)
        elif filterBy == FilterBy.EMPLID:
            if useNegate:
                return "(!(employeeID={filterCriteria})*)".format(filterCriteria=filterCriteria)
            else:
                return "(employeeID={filterCriteria}*)".format(filterCriteria=filterCriteria)
        elif filterBy == FilterBy.EMPSTATUS:
            if useNegate:
                return "(!(aliEmployeeStatus={filterCriteria}))".format(filterCriteria=filterCriteria)
            else:
                return "(aliEmployeeStatus={filterCriteria})".format(filterCriteria=filterCriteria)
        elif filterBy == FilterBy.FIRSTNAME:
            if useNegate:
                return "(!(givenName={filterCriteria}*))".format(filterCriteria=filterCriteria)
            else:
                return "(givenName={filterCriteria}*)".format(filterCriteria=filterCriteria)
        elif filterBy == FilterBy.JOBTITLE:
            if useNegate:
                return "(!(title={filterCriteria}*))".format(filterCriteria=filterCriteria)
            else:
                return "(title={filterCriteria}*)".format(filterCriteria=filterCriteria)
        elif filterBy == FilterBy.LASTNAME:
            if useNegate:
                return "(!(sn={filterCriteria}*))".format(filterCriteria=filterCriteria)
            else:
                return "(sn={filterCriteria}*)".format(filterCriteria=filterCriteria)
        else:
            if useNegate:
                return "(!(cn={filterCriteria}*))".format(filterCriteria=filterCriteria)
            else:
                return "(cn={filterCriteria}*)".format(filterCriteria=filterCriteria)
    
    def countAllADUsers(self):
        """
        Returns the count of all users in Active Directory.
        
        @return Integer
        """
        conn = self.getLdapADConnection(useSSL=True)
        if self._usetls:
            conn.start_tls()
            
        with conn as c:
            try:
                
                entry_list = c.extend.standard.paged_search(search_base=self.getBaseDNForUsers(),
                                                            search_filter='(objectclass=person)',
                                                            search_scope=SUBTREE,
                                                            attributes=None,
                                                            get_operational_attributes=False,
                                                            paged_size = 5,
                                                            generator=False)
                return len(entry_list)
            except LDAPCursorError as e:
                self._errMsg = "Critical error retrieving count of AD users. LDAPCursorError: {e}".format(e=e)
                return None;
    
    def searchADUsers(self, searchCriteria, useNegate=False, filterBy=FilterBy.NONE, attributeSet=AttributeSet.BASIC):
        """
        Search AD User entities matching search criteria.
        
        @param searchCriteria: criteria to use when performing search of users
        @type searchCriteria: String
        
        @param useNegate: indicates whether search should be structured to not include users defined by search criteria in result set
        @type useNegate: Boolean
        
        @param filterBy: filter condition to be applied to the search criteria
        @type filterBy: Enumerator of type FilterBy
        
        @param attributeSet: defines the type/number of attributes to be returned in result set. (ex. Basic, Comprehensive, All)
        @type attributeSet: Enumerator of type AttributeSet
        
        @return JSON
        """
        # Get a connection to Active Directory
        conn = self.getLdapADConnection(serverName=self._servername, domainName=self._domainname, userName=self._username, userPassword=self._userpwd, useSSL=self._usessl)
        # Start up TLS session to encrypt traffic on connection
        if self._usetls:
            conn.start_tls()
        
        if attributeSet == AttributeSet.ALL:
            attr = ALL_ATTRIBUTES
        elif attributeSet == AttributeSet.COMPREHENSIVE:
            attr = self.getExtensiveUserAttributes()
        else:
            attr = self.getBasicUserAttributes()
         
        with conn as c:
            try:            
                entry_list = c.extend.standard.paged_search(search_base=self.getBaseDNForUsers(), 
                                                            search_filter=self.getFormattedUserSearchFilter(searchCriteria, useNegate, filterBy), 
                                                            search_scope=SUBTREE, 
                                                            attributes=attr, 
                                                            get_operational_attributes=True, 
                                                            paged_size = 5, 
                                                            generator=False)
                
                return_dict = self.__createjsonfromsearch__(entry_list)
                if len(return_dict) > 0:
                    new_dict = {}
                    new_dict["employees"] = return_dict
                    return json.dumps(new_dict, indent=4, sort_keys=True, cls=DateTimeEncoder)
                else:
                    self._outMsg = "No search items returned."
                    return None

            except LDAPCursorError as e:
                self._errMsg = "Critical error searching for AD user. LDAPCursorError: {e}".format(e=e)
                return None
  
    def searchADUsersAdvanced(self, searchFilter, attributeSet=AttributeSet.BASIC):
        """
        Search AD User entities matching search criteria as defined by calling program.
        
        @param searchCriteria: criteria to use when performing search of users
        @type searchCriteria: String
        
        @param attributeSet: defines the type/number of attributes to be returned in result set. (ex. Basic, Comprehensive, All)
        @type attributeSet: Enumerator of type AttributeSet
        
        @return JSON
        """
        # Get a connection to Active Directory
        conn = self.getLdapADConnection(serverName=self._servername, domainName=self._domainname, userName=self._username, userPassword=self._userpwd, useSSL=self._usessl)
        # Start up TLS session to encrypt traffic on connection
        if self._usetls:
            conn.start_tls()
            
        if attributeSet == AttributeSet.ALL:
            attr = ALL_ATTRIBUTES
        elif attributeSet == AttributeSet.COMPREHENSIVE:
            attr = self.getExtensiveUserAttributes()
        else:
            attr = self.getBasicUserAttributes()
            
        with conn as c:
            try:
                c.search(search_base=self.getBaseDNForUsers(), search_filter=searchFilter, search_scope=SUBTREE, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
                entry_list = c.extend.standard.paged_search(search_base=self.getBaseDNForUsers(),
                                                        search_filter=searchFilter,
                                                        search_scope=SUBTREE,
                                                        attributes=attr,
                                                        get_operational_attributes=True,
                                                        paged_size = 5,
                                                        generator=False)                
                
                return_dict = self.__createjsonfromsearch__(entry_list) 
                if len(return_dict) > 0:
                    new_dict = {}
                    new_dict["employees"] = return_dict
                    return json.dumps(new_dict, indent=4, sort_keys=True, cls=DateTimeEncoder)
                else:
                    self._outMsg = "No search items returned."
                    return None
            
            except LDAPCursorError as e:
                self._errMsg = "Critical error searching for AD user. LDAPCursorError: {e}".format(e=e)
                return None
        
    def getADGroupsForUser(self, accountId):
        """
        Get the AD group memberships for a user
        
        @param accountId: the login id for the user to search for
        @type accountId: String
        
        @return JSON
        """
        conn = self.getLdapADConnection(serverName=self._servername, domainName=self._domainname, userName=self._username, userPassword=self._userpwd, useSSL=self._usessl)
        # Start up TLS session to encrypt traffic on connection
        if self._usetls:
            conn.start_tls()
            
        searchFilter = "(cn={accountId})".format(accountId=accountId)
            
        with conn as c:
            try:
                entry_list = c.extend.standard.paged_search(search_base=self.getBaseDNForUsers(),
                                                        search_filter=searchFilter,
                                                        search_scope=SUBTREE,
                                                        attributes=['memberOf'],
                                                        get_operational_attributes=False,
                                                        paged_size = 5,
                                                        generator=False)
                
                return_dict = self.__createjsonfromsearch__(entry_list, memberships=True) 
                if len(return_dict) > 0:
                    uniquelist = {}
                    uniquelist["employee"] = accountId
                    new_dict = {}
                    new_dict["groups"] = uniquelist, return_dict
                    return json.dumps(new_dict, indent=4, sort_keys=True, cls=DateTimeEncoder)
                else:
                    self._outMsg = "No search items returned."
                    return None
                
            except LDAPCursorError as e:
                self._errMsg = "Critical error searching for AD groups for {accountId}. LDAPCursorError: {e}".format(accountId=accountId, e=e)
                return None
                        
    def searchADGroups(self, searchCriteria, useNegate=False, exactMatch=True, attributeSet=AttributeSet.BASIC):
        """
        Search AD Group entities matching search criteria.
        
        @param searchCriteria: criteria to use when performing search of groups
        @type searchCriteria: String
        
        @param useNegate: indicates whether search should be structured to not include groups defined by search criteria in result set
        @type useNegate: Boolean
        
        @param exactMatch: indicates whether search should be structured to return only results with exact match to search criteria
        @type exactMatch: Boolean
               
        @param attributeSet: defines the type/number of attributes to be returned in result set. (ex. Basic, Comprehensive, All)
        @type attributeSet: Enumerator of type AttributeSet
        
        @return JSON
        """
        conn = self.getLdapADConnection(useSSL=True)
        if self._usetls:
            conn.start_tls()
        
        if useNegate and exactMatch:
            searchfilter = '!(cn={searchCriteria})'.format(searchCriteria=searchCriteria)
        elif useNegate and not exactMatch:
            searchfilter = '!(cn={searchCriteria}*)'.format(searchCriteria=searchCriteria)
        elif not useNegate and exactMatch:
            searchfilter = '(cn={searchCriteria})'.format(searchCriteria=searchCriteria)
        else:
            searchfilter = '(cn={searchCriteria}*)'.format(searchCriteria=searchCriteria)
        
        if attributeSet == AttributeSet.ALL:
            attr = ALL_ATTRIBUTES
        elif attributeSet == AttributeSet.COMPREHENSIVE:
            attr = self.getExtensiveGroupAttributes()
        else:
            attr = self.getBasicGroupAttributes()
        
        with conn as c:
            try:
                entry_list = c.extend.standard.paged_search(search_base=self.getBaseDNForGroups(),
                                                            search_filter=searchfilter,
                                                            search_scope=SUBTREE,
                                                            attributes=attr,
                                                            get_operational_attributes=True,
                                                            paged_size=5,
                                                            generator=False)
                
                return_dict = self.__createjsonfromsearch__(entry_list) 
                if len(return_dict) > 0:
                    new_dict = {}
                    new_dict["groups"] = return_dict
                    return json.dumps(new_dict, indent=4, sort_keys=True, cls=DateTimeEncoder)
                else:
                    self._outMsg = "No search items returned."
                    return None
                            
            except LDAPCursorError as e:
                self._errMsg = "Critical error searching for AD group with criteria = '{searchCriteria}'. LDAPCursorError: {e}".format(searchCriteria=searchCriteria,e=e)
                return None
            
    def getUsersForADGroup(self, groupName):
        """
        Get the user memberships for a specific AD group.
        
        @param groupName: the name of the group to get user membership for.
        @type groupName: String
        
        @return JSON
        """
        conn = self.getLdapADConnection(serverName=self._servername, domainName=self._domainname, userName=self._username, userPassword=self._userpwd, useSSL=self._usessl)
        # Start up TLS session to encrypt traffic on connection
        if self._usetls:
            conn.start_tls()
            
        searchFilter = "(cn={groupName})".format(groupName=groupName)
        with conn as c:
            try:
                entry_list = c.extend.standard.paged_search(search_base=self.getBaseDNForGroups(),
                                                        search_filter=searchFilter,
                                                        search_scope=SUBTREE,
                                                        attributes=['member'],
                                                        get_operational_attributes=False,
                                                        paged_size = 5,
                                                        generator=False)

                return_dict = self.__createjsonfromsearch__(entry_list, memberships=True)
                if len(return_dict) > 0:
                    uniquelist = {}
                    uniquelist["group"] = groupName
                    new_dict = {}
                    new_dict["employees"] = uniquelist, return_dict
                    return json.dumps(new_dict, indent=4, sort_keys=True, cls=DateTimeEncoder)
                else:
                    self._outMsg = "No search items returned."
                    return None
            
            except LDAPCursorError as e:
                self._errMsg = "Critical error searching for AD users for group {groupName}. LDAPCursorError: {e}".format(groupName=groupName, e=e)
                return None
            
    def getGroupMembershipForADGroup(self, groupName):
        """
        Get the group memberships for a specific AD group.
        
        @param groupName: the name of the group to get group membership for.
        @type groupName: String
        
        @return JSON
        """
        conn = self.getLdapADConnection(serverName=self._servername, domainName=self._domainname, userName=self._username, userPassword=self._userpwd, useSSL=self._usessl)
        # Start up TLS session to encrypt traffic on connection
        if self._usetls:
            conn.start_tls()
            
        searchFilter = "(cn={groupName})".format(groupName=groupName)
        with conn as c:
            try:
                entry_list = c.extend.standard.paged_search(search_base=self.getBaseDNForGroups(),
                                                        search_filter=searchFilter,
                                                        search_scope=SUBTREE,
                                                        attributes=['memberOf'],
                                                        get_operational_attributes=False,
                                                        paged_size = 5,
                                                        generator=False)

                return_dict = self.__createjsonfromsearch__(entry_list, memberships=True)                 
                if len(return_dict) > 0:
                    uniquelist = {}
                    uniquelist["group"] = groupName
                    new_dict = {}
                    new_dict["groups"] = uniquelist, return_dict
                    return json.dumps(new_dict, indent=4, sort_keys=True, cls=DateTimeEncoder)
                else:
                    self._outMsg = "No search items returned."
                    return None
            
            except LDAPCursorError as e:
                self._errMsg = "Critical error searching for group memberships for group {groupName}. LDAPCursorError: {e}".format(groupName=groupName, e=e)
                return None
        
    def countAllADGroups(self):
        """
        Returns the count of all groups in Active Directory
        
        @return Integer
        """
        conn = self.getLdapADConnection(useSSL=True)
        if self._usetls:
            conn.start_tls()
        
        with conn as c:
            try:
                entry_list = c.extend.standard.paged_search(search_base=self.getBaseDNForGroups(),
                                                            search_filter='(objectclass=group)',
                                                            search_scope=SUBTREE,
                                                            attributes=None,
                                                            get_operational_attributes=False,
                                                            paged_size = 5,
                                                            generator=False)
            
                return len(entry_list)
            
            except LDAPCursorError as e:
                self._errMsg = "Critical error retrieving count of AD groups. LDAPCursorError: {e}".format(e=e)
                return None
            
    def __createjsonfromsearch__(self, caseinsensitivedict, memberships=False):
        """
        Creates a JSON object using the case insensitive dictionary passed into the method.
                
        @param caseinsensitivedict: a case insensitive dictionary with results from an AD user or AD group search.
        @type caseinsensitivedict: CaseInsensitiveDict
               
        @param memberships: indicates if the calling method wants to retrieve group membership information.
        @type memberships: Boolean
        
        @return Dictionary
        """
        results_dict = {}
        for result in caseinsensitivedict:
            result_attr = result['attributes']
            for key, value in result_attr.items():
                if not memberships:
                    results_dict[key] = value
                else:
                    newlist = []
                    for mbr in value:
                        membrstr = re.findall(r'CN\=([^\,]+)', mbr)
                        newstr = membrstr[0]
                        newlist.append(newstr)
                    
                    results_dict[key] = newlist
        
        return results_dict
        
if __name__ == "__main__":
    print("Module Name: AD")
    ldap_server = 'ldapdev.alliant-energy.com'
    domain_name = 'ali'
    
    print("Prompting for credentials to connect to domain '{domain_name}' on ldap server '{ldap_server}'.".format(domain_name=domain_name, ldap_server=ldap_server))
    user_name = input("Username: ")
    user_pwd = input("Password: ")
    a = ActiveDirectory(serverName=ldap_server, domainName=domain_name, userName=user_name, userPassword=user_pwd)
    a.useTLSConnection(False)
    
    print("Querying {domain_name} domain on server {ldap_server}...".format(domain_name=domain_name, ldap_server=ldap_server))
    
    user_count = a.countAllADUsers()
    print("There are {user_count} AD users.".format(user_count=user_count))
    user_groups = a.countAllADGroups()
    print("There are {user_groups} AD groups.".format(user_groups=user_groups))
    print("Done.")