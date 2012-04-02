#!/usr/bin/env python
import sys
import os
import uuid
import asyncore
import threading
import smtpd
import time
import email
import re

# written by thomas fischer thomas{AT}thomasfischer{DOT}biz
# idea based on http://code.activestate.com/recipes/440690/
# ~ yeah, and then we added some stuff here and there ~

mailPassword = ''
with open('password') as f:
    mailPassword = f.read().strip()

CONTENT_RE = re.compile('image/(jpeg|png|gif)', re.I)

if not os.path.exists("snippets"):
    os.system("mkdir snippets")
    
if (os.system("wkhtmltopdf --version > /dev/null") != 0):
    print("This script requires wkhtmltopdf, stopping now.")
    exit(1)
    
if (os.system("convert --version > /dev/null") != 0):
    print("This script requires ImageMagick (convert), stopping now.")
    exit(1)
    
def handleMessage(message_str, guid = None):
    message = email.message_from_string(message_str)

    if guid == None:
        guid = str(uuid.uuid4())
    with open('snippets/' + guid + '.txt', 'w') as fout:
        fout.write(message_str)
        
    imageContent = ''
    imageFilename = ''
    messageHtml = ''

    for part in message.walk():
        charset = part.get_charset()
        if charset == None:
            charset = part.get_content_charset()
        if part.get_content_type() == 'text/plain':
            messageHtml = "<p>" + unicode(part.get_payload(decode = True), charset, 'replace') + "</p>"
        elif part.get_content_type() == 'text/html':
            if len(messageHtml) == 0:
                messageHtml = unicode(part.get_payload(decode = True), charset, 'replace')
        else:
            try:
                if CONTENT_RE.search(part.get_content_type()) and part.get_filename():
                    thisContent = part.get_payload(None, True)
                    if len(thisContent) > len(imageContent):
                        imageFilename = ''
                        if part.get_content_type() == 'image/jpeg':
                            imageFilename = '.jpg'
                        elif part.get_content_type() == 'image/png':
                            imageFilename = '.png'
                        elif part.get_content_type() == 'image/gif':
                            imageFilename = '.gif'
                        imageFilename = 'image' + imageFilename
                        imageContent = part.get_payload(None, True)
            except:
                pass
                
    if len(imageContent) > 0:
        with open('snippets/' + guid + imageFilename, 'wb') as fout:
            fout.write(imageContent)
            
    htmlPath = 'snippets/' + guid + '.html'
    pdfPath = 'snippets/' + guid + '.pdf'
    pbmPath = 'snippets/' + guid + '.pbm'
    pngPath = 'snippets/' + guid + '.png'
    if not os.path.exists(pbmPath):
        with open(htmlPath, 'w') as fout:
            fout.write("<html><head><link href='../styles.css' type='text/css' rel='stylesheet' media='all' /></head><body><div class='post'>\n")
            #fout.write("<img class='qr' src='http://qrcode.kaywa.com/img.php?s=12&d=http%3A%2F%2Fwww.faz.net%2F-gum-6y6jv' />\n")
            if len(message['subject'].strip()) > 0:
                fout.write("<h1>" + message['subject'].encode('utf-8') + "</h1>\n\n")
            fout.write(messageHtml.encode('utf-8') + "\n\n")
            if len(imageContent) > 0:
                fout.write("<img src='" + guid + imageFilename + "' />\n\n")
            fout.write("</div><!--<center><img src='../hr.png' style='width: 30%;'/></center>--></body></html>\n")
        os.system("wkhtmltopdf --encoding utf8 --page-width 48 --page-height 3000 -B 0 -L 0 -T 0 -R 0 \"" + htmlPath + "\" \"" + pdfPath + "\" 2> /dev/null")
        os.system("convert +antialias -density 202  \"" + pdfPath + "\" -trim -extent 384x -equalize -monochrome \"" + pbmPath + "\"");
        os.system("convert \"" + pbmPath + "\" \"" + pngPath + "\"");
        os.system("rm \"" + htmlPath + "\"")
        os.system("rm \"" + pdfPath + "\"")
        os.system("rm \"" + pbmPath + "\"")

    if len(imageContent) > 0:
        os.system("rm " + 'snippets/' + guid + imageFilename)
        
    print("Arduino, print this file: snippets/" + guid + ".pbm !!1!")
    print("Sending reply to " + message['from'] + "...")
    os.system("sendEmail -f hardcopythat@gmail.com -t \"" + message['from'] + "\" -u \"Re: " + message['subject'] + "\" -s smtp.gmail.com -o tls=yes -xu hardcopythat -xp \"" + mailPassword + "\" -m \"Copy that!\" -a \"" + pngPath + "\"")
    #raise StandardError()

class MySMTPServer(smtpd.SMTPServer):
    def __init__(self, localaddr, remoteaddr):
        smtpd.SMTPServer.__init__(self, localaddr, remoteaddr)

    def process_message(self, peer, mailfrom, rcpttos, data):
        try:
            handleMessage(data)
        except:
            pass

class MyEmailServer(threading.Thread):
    def __init__(self, ipport):
        threading.Thread.__init__(self)
        self._stopevent = threading.Event()
        self.server = MySMTPServer(ipport, None)

    def run(self):
        while not self._stopevent.isSet():
            asyncore.loop(timeout = 0.001, count = 1)

    def stop(self, timeout=None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)
        self.server.close()

if __name__ == "__main__":
    
    #s = ''
    #with open('snippets/0b403f73-6424-472b-9454-2600beac2593.txt') as f:
        #s = f.read()
    #handleMessage(s, '0b403f73-6424-472b-9454-2600beac2593')
    #exit(1)

    if len(sys.argv) != 2:
        print "usage: ip:port"
        sys.exit(1)

    ar = sys.argv[1].split(":")
    ar[1] = int(ar[1])
    ipport = tuple(ar)
    mailServer = MyEmailServer(ipport)
    mailServer.start()
    print "running"
    running = True
    while running:
        try:
            time.sleep(1)
        except:
            print "stopping"
            mailServer.stop()
            del mailServer
            running = False