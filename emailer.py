#! /usr/bin/python36
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
#[]  Script: email.py                                                          []
#[]  Script Language: Python 3.6(.4)                                           []
#[]  Description: This class can be used to send html or text email with or    []
#[]               without an attachment.                                       []
#[]  Author: Paul J. Laue                                                      []
#[]  Created: February 15, 2018 02:03:00 PM                                    []
#[] ========================================================================== []
#[]  CHANGE LOG                                                                []
#[]  ----------                                                                []
#[]                                                                            []
#[] ========================================================================== []
#[][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][][]
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
import re
import smtplib
from enum import Enum

class Distribution(Enum):
    """
    A custom enumerator that defines how distribution should occur within a calling program. (ex. EMAIL, REMOTE TRANSMISSION, etc.)
    """
    EMAIL = 1,
    REMOTE = 2

class Email:
    """
    This class handles the creation and sending of email messages
    via SMTP.  This class also handles attachments and can send
    HTML messages.  The code comes from various places around
    the net and from my own brain.
    """
    def __init__(self, smtpServer):
        """
        Create a new empty email message object.

        @param smtpServer: The address of the SMTP server
        @type smtpServer: String
        """
        self._textBody = None
        self._htmlBody = None
        self._subject = ""
        self._smtpServer = smtpServer
        self._reEmail = re.compile("^([\\w \\._]+\\<[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\>|[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)$")
        self.clearRecipients()
        self.clearAttachments()
        self._errMsg = ''
        self._outMsg = ''
        
    def send(self):
        """
        Send the email message represented by this object.
        """
        # Validate message
        if self._textBody is None and self._htmlBody is None:
            raise Exception("Error! Must specify at least one body type (HTML or Text)")
        if len(self._to) == 0:
            raise Exception("Must specify at least one recipient")
        
        # Create the message part
        if self._textBody is not None and self._htmlBody is None:
            msg = MIMEText(self._textBody, "plain")
        elif self._textBody is None and self._htmlBody is not None:
            msg = MIMEText(self._htmlBody, "html")
        else:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(self._textBody, "plain"))
            msg.attach(MIMEText(self._htmlBody, "html"))
            
        # Add attachments, if any
        if len(self._attach) != 0:
            tmpmsg = msg
            msg = MIMEMultipart()
            msg.attach(tmpmsg)
            
        for fname,attachname in self._attach:
            if not os.path.exists(fname):
                self._errMsg = "File '{fname}' does not exist. Not attaching to email.".format(fname=fname)
                continue
            if not os.path.isfile(fname):
                self._errMsg = "Attachment '{fname}' is not a file. Not attaching to email.".format(fname=fname)
                continue
            
            # Guess at encoding type
            ctype, encoding = mimetypes.guess_type(fname)
            if ctype is None or encoding is not None:
                # No guess could be made so use a binary type.
                ctype = 'application/octet-stream'
            
            maintype, subtype = ctype.split('/', 1)
            if maintype == 'text':
                fp = open(fname)
                attach = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'image':
                fp = open(fname, 'rb')
                attach = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(fname, 'rb')
                attach = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(fname, 'rb')
                attach = MIMEBase(maintype, subtype)
                attach.set_payload(fp.read())
                fp.close()
                # Encode the payload using Base64
                encoders.encode_base64(attach)
            
            # Set the filename parameter
            if attachname is None:
                filename = os.path.basename(fname)
            else:
                filename = attachname
                
            attach.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attach)
            
        # Some header stuff
        msg['Subject'] = self._subject
        msg['From'] = self._from
        msg['To'] = ", ".join(self._to)
        msg.preamble = "You need a MIME enabled mail reader to see this message"
        
        # Send message
        msg = msg.as_string()
        with smtplib.SMTP(self._smtpServer) as svr:
            svr.sendmail(self._from, self._to, msg)            
       
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
            
    def setSubject(self, subject):
        """
        Set the subject of the email message.
        """
        self._subject = subject
        
    def setFrom(self, address):
        """
        Set the email sender.
        """
        if not self.validateEmailAddress(address):
            raise Exception("Invalid email address {address}".format(address=address))
        self._from = address
        
    def clearRecipients(self):
        """
        Remove all currently defined recipients for
        the email message.
        """
        self._to = []
        
    def addRecipient(self, address):
        """
        Add a new recipient to the email message.
        """
        if not self.validateEmailAddress(address):
            raise Exception("Invalid email address '{address}'!".format(address=address))
        self._to.append(address)
    
    def setTextBody(self, body):
        """
        Set the plain text body of the email message.
        """
        self._textBody = body
    
    def setHtmlBody(self, body):
        """
        Set the HTML portion of the email message.
        """
        self._htmlBody = body
        
    def clearAttachments(self):
        """
        Remove all file attachments.
        """
        self._attach = []
    
    def addAttachment(self, fname, attachname=None):
        """
        Add a file attachment to this email message.

        @param fname: The full path and file name of the file
                      to attach.
        @type fname: String
        @param attachname: This will be the name of the file in
                           the email message if set.  If not set
                           then the filename will be taken from
                           the fname parameter above.
        @type attachname: String
        """
        if fname is None:
            return
        self._attach.append((fname, attachname))
        
    def validateEmailAddress(self, address):
        """
        Validate the specified email address.
        
        @param attachname: name of file to attach
        @type attachname: String
        
        @return: True if valid, False otherwise
        @type: Boolean
        """
        if self._reEmail.search(address) is None:
            return False
        return True
    
if __name__ == "__main__":
    # Run some tests
    mFrom = "DoNotReply <donotreply@alliantenergy.com>"
    mTo = "paullaue@alliantenergy.com"
    m = Email("mailgate@alliantenergy.com")
    m.setFrom(mFrom)
    m.addRecipient(mTo)
    
    # Simple Plain Text Email
    m.setSubject("Plain text email")
    m.setTextBody("This is a plain text email <b>I should not be bold</b>")
    m.send()
    
    # Plain text + attachment
    m.setSubject("Text plus attachment")
#    m.addAttachment("/home/user/image.png")
    m.send()
    
    # Simple HTML Email
    m.clearAttachments()
    m.setSubject("HTML Email")
    m.setTextBody(None)
    m.setHtmlBody("The following should be <b>bold</b>")
    m.send()
    
    # HTML + attachment
    m.setSubject("HTML plus attachment")
#    m.addAttachment("/home/user/image.png")
    m.send()

    # Text + HTML
    m.clearAttachments()
    m.setSubject("Text and HTML Message")
    m.setTextBody("You should not see this text in a MIME aware reader")
    m.send()
    
    # Text + HTML + attachment
    m.setSubject("HTML + Text + attachment")
#    m.addAttachment("/home/user/image.png")
    m.send()