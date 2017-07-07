#!/usr/bin/env python
# encoding: utf-8
import sys, io, os, re
import codecs
import shutil
import logging
import sqlite3
import zipfile
import subprocess
from bs4 import BeautifulSoup

ROOT = './OUT'
NOTES = './notes/'
ATTACHMENTS = './attachments/'

PYINTERPRETER = "/usr/bin/python3" 
HTML2TEXT = "./lib/html2text.py"

def unzip(src, dst):
    zip_file = zipfile.ZipFile(src)
    for names in zip_file.namelist():
        zip_file.extract(names, dst)
    zip_file.close()

def rmExtname(filename):
    (shortname, extension) = os.path.splitext(filename)
    return shortname

def makePath(path):
    flag = os.path.exists(path)
    if not flag: 
        os.makedirs(path)
    return flag 

def readFromDB(dbname, sql):
    mydb = sqlite3.connect(dbname)
    cursor = mydb.cursor()
    cursor.execute(sql)
    table = cursor.fetchall()
    return table

def addInitURL(htmlname):
    print(htmlname)
    html = codecs.open(htmlname, 'rb', 'utf-8')
    soup = BeautifulSoup(html, "lxml")
    body = soup.body
    a_tag = body.new_tag("a", href = "www.example.com") 
    body.insert(0, a_tag)
    newhtml = codecs.open('new-' + htmlname, 'wb', 'utf-8')
    newhtml.write(str(soup))
    newhtml.close()
    html.close()

def wrapMarkdown(filepath, mdpath):
    pargs = [PYINTERPRETER, HTML2TEXT, filepath, '1>'+mdpath]
    os.system(' '.join(pargs))


def copyNotes(table):
    for row in table:
        hash, title, location, notename, url = row
        notename = rmExtname(notename)
        spath = NOTES + '{' + hash + '}'
        dpath = ROOT + location + notename
        if notename.endswith('.md'):
            dpath = dpath + '.md'
        makePath(dpath)
        if url:    
            print(url)
            #addInitURL(dpath + '/index.html')
        try:
            unzip(spath, dpath)
            print('[UNZIP]\t' + spath + '->' + dpath)
            if notename.endswith('.md'):
                wrapMarkdown(dpath + '/index.html', ROOT + location + notename)
                shutil.rmtree(dpath)
        except Exception as e:
            print(e)

def copyAttachments(table):
    for row in table:
        hash, location, notename, attname = row
        notename = rmExtname(notename)
        makePath(ROOT + location + notename)
        spath = ATTACHMENTS + '{' + hash + '}' + attname
        dpath = ROOT + location + notename + '/' + attname
        try:
            shutil.copyfile(spath, dpath)
            print('[INFO]\t' + spath)
        except Exception as e:
            print(e)
            #print('[ERROR]\t' + spath)
        
def main():
    sql_note = "select DOCUMENT_GUID, DOCUMENT_TITLE, DOCUMENT_LOCATION, DOCUMENT_NAME, DOCUMENT_URL from WIZ_DOCUMENT"
    sql_attach = "select ATTACHMENT_GUID, DOCUMENT_LOCATION, DOCUMENT_NAME, ATTACHMENT_NAME from WIZ_DOCUMENT, WIZ_DOCUMENT_ATTACHMENT where  WIZ_DOCUMENT.DOCUMENT_GUID = WIZ_DOCUMENT_ATTACHMENT.DOCUMENT_GUID"
    notes = readFromDB("index.db", sql_note)
    copyNotes(notes)
    '''
    atttachments = readFromDB("index.db", sql_attach)
    copyAttachments(atttachments)  
    '''
if __name__ == "__main__":
    main()