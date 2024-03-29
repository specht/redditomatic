#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.dom.minidom import parse, parseString
import os
from subprocess import *

output = Popen(["wget", "-q", "-O", "/dev/stdout", "http://www.faz.net/aktuell/?rssview=1"], stdout=PIPE).communicate()[0]
dom = parseString(output)

if not os.path.exists("snippets"):
    os.system("mkdir snippets")
    
if (os.system("wkhtmltopdf --version > /dev/null") != 0):
    print("This script required wkhtmltopdf, stopping now.")
    exit(1)
    
if (os.system("convert --version > /dev/null") != 0):
    print("This script required ImageMagick (convert), stopping now.")
    exit(1)
    
def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)
    
for item in dom.getElementsByTagName('item'):
    guid = getText(item.getElementsByTagName('guid')[0].childNodes)
    guid = guid.replace('/', '_')
    htmlPath = 'snippets/' + guid + '.html'
    pdfPath = 'snippets/' + guid + '.pdf'
    pbmPath = 'snippets/' + guid + '.pbm'
    if not os.path.exists(pbmPath):
        with open(htmlPath, 'w') as fout:
            fout.write("<html><head><link href='../styles.css' type='text/css' rel='stylesheet' media='all' /></head><body><div class='post'>\n")
            #fout.write("<img class='qr' src='http://qrcode.kaywa.com/img.php?s=12&d=http%3A%2F%2Fwww.faz.net%2F-gum-6y6jv' />\n")
            fout.write("<h1>" + getText(item.getElementsByTagName('title')[0].childNodes).encode('utf-8') + "</h1>\n\n")
            fout.write(getText(item.getElementsByTagName('description')[0].childNodes).encode('utf-8') + "\n\n")
            fout.write("</div><center><img src='../hr.png' style='width: 30%;'/></center></body></html>\n")
        os.system("wkhtmltopdf --encoding utf8 --page-width 48 --page-height 3000 -B 0 -L 0 -T 0 -R 0 \"" + htmlPath + "\" \"" + pdfPath + "\"")
        os.system("convert +antialias -density 219 \"" + pdfPath + "\" -trim -monochrome \"" + pbmPath + "\"");
        os.system("rm \"" + htmlPath + "\"")
        os.system("rm \"" + pdfPath + "\"")
