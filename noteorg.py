#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package noteorg
#  
#  \brief Note Organizer the file header
#
#  ### The file header follows this format
#
# > &lt;!-- <br>
# >  +Author: 刘嘉屹 <br>
# >  +Date Created: 16 Jan 2014 <br>
# >  +Date Changed: <br>
# >  +Tags: General; Chinese; <br>
# >  +标签: 通用 <br>
# > --&gt;
#
#  ### JSON data structure
# 
#  *object*
#
#  > { <br>
#  > "Author": xxx, <br>
#  > "Date_create": xxx, <br>
#  > "Date_change": xxx, <br>
#  > "tags": [xxx,xxx,xxx], <br>
#  > "ctags": [xxx,xxx,xxx], <br>
#  > "content": xxx <br>
#  > }
#


from os.path import isfile,abspath,basename,getmtime
import sys
import sqlite3 as sql
import glob
import re
from time import localtime, strftime,strptime

from systools import *

# set for python 2.7 version
reload(sys)
sys.setdefaultencoding("UTF-8")

##
#  \brief Class for markdown file note
#  \details This class build to load the file into program and support multiple output formats
#  \date 2014-01-17
class Note:
    ##
    # \brief Initialization code
    # \param path path to the file (the last */* is needed)
    # \param filename name string of a file to load-in
    # \param fulltext if set, then create the Note from input text
    def __init__(self,path,filename,fulltext=[]):
        try:
            ## Filename of the Note
            self.filename = unicode(filename)
            ## Path to Note
            self.path = unicode(path)
            #if self.path[-1]!='/':
            #    self.path = str.append(self.path,'/')
            
            filename = self.path+self.filename
            if len(fulltext) == 0: # create new Note from file
                # !!! Exam file existency !!! #
                if not isfile(filename):
                    raise Exception("!! Fail to open %s !!"%filename)
                # !!! initial empty content !!! #
                ## Author of the Note 
                self.author = unicode("EMPTY")
                ## Create Date of the Note
                self.dateCreate = None
                ## Create Date of the Note
                self.dateChange = None
                ## system last modification time
                self.modifyTime = localtime(getmtime(filename))
                ## Tags for the Note
                self.tags = []
                ## Tags for the Note (Chinese)
                self.ctags = []
                ## Main content of the Note
                self.content = ''
                # !!! Load file content !!! #
                with open(filename,'r') as f:
                    fulltext = f.readlines()
                    # !!! empty file case !!! #
                if len(fulltext) == 0:
                    raise Exception("!! File %s is empty"%filename)
            else: # the fulltext is loaded from database
                # !!! empty Database case !!! #
                if len(fulltext) == 0:
                    raise Exception("!! Database item %s is empty"%filename)
            # !!! phrasing content !!! #
            self.phraseContent(fulltext)
        except Exception as inst:
            warning("!!Note"+inst.args[0])
            if inst.args[0][:2] == "!!":
                raise Exception("NoteClass","!!Fail to initialize Note class from %s"%self.filename)
            else:
                raise
    ##
    # \brief phrase the whole content
    def phraseContent(self,fulltext):
        if fulltext[0].strip(NEWLINE) != "<!--":
            raise Exception("!! Fail to recognize header from: %s"
                            %fulltext[0].strip(NEWLINE))
        finishFlag = False
        for ii,line in enumerate(fulltext[1:]):
            if (line.strip(NEWLINE) == "-->"):
                finishFlag = ii
                break
            # !!! Start pumping header !!! #
            currentName = ''
            if line[0] == '+':  # identify header
                ia = line.find(':')
                ib = line.find("：")
                if not (ia & ib):
                    raise Exception("!! Not seperator in header !!")
                ia = ia if ia != -1 else 100000
                ib = ib if ib != -1 else 100000
                if ib > ia: # choose the smallest
                    currentName = line[1:ia]
                    self.__populateHeaderObj(currentName,line[ia+1:])
                else:
                    currentName = line[1:ib]
                    self.__populateHeaderObj(currentName,line[ib+3:])
            elif currentName != '': # continue previous header
                self.__populateHeaderObj(currentName,line)
            else:  # unrecognized case
                warning("unknown case:: %s"%line)
        if not finishFlag:
            raise Exception("!! Unfinished header !!")
        # !!! insert main body !!! #
        if len(fulltext) == ii+2:
            raise Exception("!! Empty Content !!")
        self.content = unicode("".join(fulltext[ii+2:]))

    ##
    # \brief Populate the header content into Note class
    # \param name the keyword
    # \param content string contains all keywords
    def __populateHeaderObj(self,name,content):
        content = content.strip() # remove leading and trailing spaces
        if name.lower() == "author": 
            self.author = unicode(content)
        if name.lower() == "date created":
            if content == "":
                self.dateCreate = localtime()
            else:
                self.dateCreate = strptime(content,"%d %b %Y")
        if name.lower() == "date changed":
            if content == "":
                self.dateChange = self.dateCreate
            else:
                self.dateChange = strptime(content,"%d %b %Y")
        if name.lower() == "tags":
            self.__populateTagArray(content)
        if name.lower() == "标签":
            self.__populateTagArrayS(content)
        return

    ##
    # \brief Populate the header tags array, work only for or ";"
    # \param content a ;-seperated list of tags
    def __populateTagArray(self,content):
        self.tags = re.split(';+', content)
        self.tags = [unicode(x.strip().capitalize()) for x in self.tags if x]
        return
    
    ##
    # \brief Populate the header ctags array, work only for or ";" and "；" 中文标签
    # \param content a ;-seperated list of tags
    #  Populate the header tag array, work only for  or ";"
    def __populateTagArrayS(self,content):
        self.ctags = re.split(';+|；+', content)
        self.ctags = [unicode(x.strip().capitalize()) for x in self.ctags if x]
        return 
    ##
    # \brief return header information in one string
    def returnHeader(self):
        str = "<!--\n" + \
            "+Author: %s"%self.author + NEWLINE + \
            "+Date Created: %s"%strftime("%d %b %Y",self.dateCreate) + NEWLINE + \
            "+Date Changed: %s"%strftime("%d %b %Y",self.dateChange) + NEWLINE + \
            "+Tags: %s"%";".join(self.tags) + NEWLINE + \
            "+标签: %s"%";".join(self.ctags) + NEWLINE + \
            "-->\n"
        return str

    ##
    # \brief write Note into file
    # \param filename name of the file to write in (need to be a new file)
    def writeFile(self,filename):
        try:
            if isfile(filename):
                raise Exception("!! File (%s)Exist; Stop to overwrite !!"%filename)
            with open(filename,'w') as f:
                f.write(self.returnHeader()+self.content)
        except Exception as inst:
            warning(inst.args[0])
            raise
            #sys.exit(1)
        return
               
## 
# \class IndexPage
# \brief index all Note classes
# 
# Create an index page contains all tags and filename(link)
class IndexPage:
    pass
                        
##
# \class NoteDB
# \brief interface of database
# \date 2014-01-20
#
#  head - store file header
#  content -store note content
#  tag - store file tags
#  ctag - store chinese tags
#
#  main function:
#
#  + import(): import a new path into database (no file conflict checking)
#  + update(): update a path which contains files already in database
#  + getFileByTag():  get file names by tag
#  + getContent(): get file content by file name
#
#  ### Database entry
#  
#  *table*
#
#   + head
#
#   --------------------------------------
#   | Name         | Type                |
#   |------------- |---------------------|
#   | fid          | INTEGER PRIMARY KEY |
#   | filename     | TEXT                |
#   | path         | TEXT                |
#   | author       | TEXT                |
#   | date_create  | TEXT                |
#   | date_change  | TEXT                |
#   | sys_modified | TEXT                |
#   --------------------------------------
#
#        UNIQUE (filename,path)
#
#   + content
#
#   ----------------------------------------------------------
#   | Name    | Type                                         |
#   |---------|----------------------------------------------|
#   | fid     | INTEGER NOT NULL PRIMARY KEY REFERENCES head |
#   | content | TEXT                                         |
#   ----------------------------------------------------------
#
#   + tag
#
#   ----------------------------------------------------------
#   | Name   | Type                                          |
#   |--------|-----------------------------------------------|
#   | tid | INTEGER NOT NULL PRIMARY KEY                     |
#   | tag | TEXT UNIQUE                                      |
#   ----------------------------------------------------------
#
#   + ctag
#
#   ----------------------------------------------------------
#   | Name   | Type                                          |
#   |--------|-----------------------------------------------|
#   |ctid |INTEGER NOT NULL PRIMARY KEY|
#   |ctag |TEXT UNIQUE|
#   --------------------
#
#   + tf_bridge
#
#   ----------------------------------------------------------
#   | Name   | Type                                          |
#   |--------|-----------------------------------------------|
#   | fid | INTEGER NOT NULL REFERENCES head                 |
#   | tid | INTEGER NOT NULL REFERENCES tag                  |
#   ----------------------------------------------------------
#
#        PRIMARY KEY (fid,tid)
#
#   + ctf_bridge
#
#   ----------------------------------------------------------
#   | Name   | Type                                          |
#   |--------|-----------------------------------------------|
#   | fid    | INTEGER NOT NULL REFERENCES head              |
#   | ctid   | INTEGER NOT NULL REFERENCES ctag              |
#   ----------------------------------------------------------
#
#        PRIMARY KEY (fid,ctid)
#
class NoteDB():
    ## 
    # initialize the NoteDB class
    #  \param filename file name of the database
    #    if file exist, then read the database, otherwise ask to create one
    def __init__(self,filename):
        if isfile(filename):
            ## SQL connector
            self.conn = sql.connect(filename)
            self.conn.text_factory = str
            ## SQL cursor
            self.cur = self.conn.cursor() 
        else:
            s = raw_input(">> Create a database '%s'? [n]/y: "%filename)
            if s != 'y':
                sys.exit(1)
            path = raw_input(">> Input the path of md files: ")
            self.__createDB(filename)
            self.__importDB(path)

    ## destructor of NoteDB class
    #
    def __del__(self):
        if hasattr( self, "conn"):
            self.conn.close()
        
    ##
    # create a empty database        
    # \param filename file name of the database
    # \todo add time stamp
    def __createDB(self,filename):
        self.conn = sql.connect(filename)
        c = self.conn.cursor()
        c.executescript(''' CREATE TABLE head
        (
        fid INTEGER PRIMARY KEY,
        filename TEXT,
        path TEXT,
        author TEXT,
        date_create TEXT,
        date_change TEXT,
        sys_modified TEXT,
        UNIQUE (filename,path)
        );
        CREATE TABLE content
        (
        fid INTEGER NOT NULL PRIMARY KEY REFERENCES head,
        content TEXT
        );
        CREATE TABLE tag
        (
        tid INTEGER NOT NULL PRIMARY KEY,
        tag TEXT UNIQUE
        );
        CREATE TABLE ctag
        (
        ctid INTEGER NOT NULL PRIMARY KEY,
        ctag TEXT UNIQUE
        );
        CREATE TABLE tf_bridge
        (
        fid INTEGER NOT NULL REFERENCES head,
        tid INTEGER NOT NULL REFERENCES tag,
        PRIMARY KEY (fid,tid)
        );
        CREATE TABLE ctf_bridge
        (
        fid INTEGER NOT NULL REFERENCES head,
        ctid INTEGER NOT NULL REFERENCES ctag,
        PRIMARY KEY (fid,ctid)
        )
        ''')
        self.conn.commit()
        self.cur = c

    ##
    # expend the current database by given path
    # \param path path to md files
    def __importDB(self,path):
        path = abspath(path)+'/' # extend to full path
        files = glob.glob(path+"*.md")
        for ifile in files:
            try:
                ifile = basename(ifile)
                print "- Insert "+ifile
                inote = Note(path,ifile)
                self.insertNote(inote)
            except Exception as inst:
                if (len(inst.args) == 2) and (inst.args[0]=="NoteClass"): # read-in fail
                    warning(inst.args[1])
                else: # other problems
                    raise
        self.conn.commit()

    ##
    # insert a Note Class
    # \param note a Note Class
    def insertNote(self,note):
        # insert header
        self.cur.execute('''INSERT INTO
        head (filename,path,author,date_create,date_change,sys_modified)
        VALUES (?,?,?,?,?,?)''',
        [note.filename, note.path, note.author,
         strftime("%Y-%m-%d",note.dateCreate),
         strftime("%Y-%m-%d",note.dateChange),
         strftime("%Y-%m-%d %H:%M:%S",note.modifyTime)
        ])
        self.cur.execute("SELECT last_insert_rowid()")
        fid = self.cur.fetchone()[0]
        # insert content
        self.cur.execute("INSERT INTO content VALUES (?,?)",[fid,unicode(note.content)])
        # insert tag and tf_bridge
        for itag in note.tags:
            self.cur.execute("INSERT INTO tag (tag) select (?) where not exists(select tid from tag where tag=?)",[itag,itag])
            self.cur.execute("select tid from tag where tag =?",[itag]);
            tid = self.cur.fetchone()[0]
            self.cur.execute("INSERT INTO tf_bridge (fid,tid) VALUES (?,?)",[fid,tid])
        # insert ctag and ctf_bridge
        for itag in note.ctags:
            itag = unicode(itag)
            self.cur.execute("INSERT INTO ctag (ctag) select (?) where not exists(select ctid from ctag where ctag=?)",[itag,itag])
            self.cur.execute("select ctid from ctag where ctag =?",[itag]);
            tid = self.cur.fetchone()[0]
            self.cur.execute("INSERT INTO ctf_bridge (fid,ctid) VALUES (?,?)",[fid,tid])
            
    ##
    # update a Note Class
    # \param note Note class
    def updateNote(self,note):
        # examine whether note is already in the database
        self.cur.execute("SELECT fid FROM head WHERE filename == ? AND path == ?",
                                 [note.filename,note.path])
        s = self.cur.fetchone()
        if s is None: # new Note
                warning("- Insert "+note.filename,color=33)
                self.insertNote(note)
        else: # Note exist
            self.cur.execute("SELECT fid from head WHERE fid == ? AND sys_modified < ?"
                ,[s[0],strftime("%Y-%m-%d %H:%M:%S",note.modifyTime)])
            s = self.cur.fetchone()
            # Note need to be updated
            if s is not None:
                fid = s[0]                
                warning("- Updating "+note.filename,color=32)
                # update head
                self.cur.execute('''UPDATE head SET filename = ?, path = ?,
                author = ?, date_create = ?, date_change = ?, sys_modified = ?
                WHERE fid = ?''',
                [ note.filename, note.path, note.author,
                strftime("%Y-%m-%d",note.dateCreate),
                strftime("%Y-%m-%d",note.dateChange),
                strftime("%Y-%m-%d %H:%M:%S",note.modifyTime),
                fid
                ])
                # update content
                self.cur.execute("UPDATE content SET content = ? where fid = ?",[note.content,fid])
                # update tags
                pendingtags = note.tags
                self.cur.execute("SELECT tag, tid FROM tf_bridge JOIN tag USING (tid) WHERE fid = ?",[fid])
                tagsindb = self.cur.fetchall()
                for itag in tagsindb:
                    if itag[0] in pendingtags: # in tag list
                        pendingtags.remove(itag[0])
                    else: # remove from database
                        self.cur.execute("DELETE FROM tf_bridge WHERE fid = ? AND tid = ?",[fid,itag[1]])
                for itag in pendingtags: # add new tags
                    self.cur.execute("INSERT INTO tag (tag) SELECT (?) WHERE NOT EXISTS(SELECT tid FROM tag WHERE tag=?)",[itag,itag])
                    self.cur.execute("SELECT tid FROM tag WHERE tag =?",[itag]);
                    tid = self.cur.fetchone()[0]
                    self.cur.execute("INSERT INTO tf_bridge (fid,tid) VALUES (?,?)",[fid,tid])
                # update ctags
                pendingtags = note.ctags
                self.cur.execute("SELECT ctag, ctid FROM ctf_bridge JOIN ctag USING (ctid) WHERE fid = ?",[fid])
                tagsindb = self.cur.fetchall()
                for itag in tagsindb:
                    if itag[0] in pendingtags: # in tag list
                        pendingtags.remove(itag[0])
                    else: # remove from database
                        self.cur.execute("DELETE FROM ctf_bridge WHERE fid = ? AND ctid = ?",[fid,itag[1]])
                for itag in pendingtags: # add new tags
                    self.cur.execute("INSERT INTO ctag (ctag) SELECT (?) WHERE NOT EXISTS(SELECT ctid FROM ctag WHERE ctag=?)",[itag,itag])
                    self.cur.execute("SELECT ctid FROM ctag WHERE ctag =?",[itag]);
                    tid = self.cur.fetchone()[0]
                    self.cur.execute("INSERT INTO ctf_bridge (fid,ctid) VALUES (?,?)",[fid,tid])
                    
    ##
    # update the database for given directory
    # \param path path to the notes files
    def updateDB(self,path):
        path = abspath(path)+'/' # extend to full path
        files = glob.glob(path+"*.md")
        for ifile in files:
            try:
                ifile = basename(ifile)
                inote = Note(path,ifile)
                self.updateNote(inote)
            except Exception as inst:
                if (len(inst.args) == 2) and (inst.args[0]=="NoteClass"): # read-in fail
                    warning(inst.args[1])
                else: # other problems
                    raise
        self.conn.commit()

    ##
    # \brief clean up to make the database tight
    #
    #  clean the tag/tags which are not available in bridge table anymore.
    def cleanTag(self):
        self.cur.execute("DELETE FROM tag WHERE tid IN ( SELECT tid from tag LEFT OUTER JOIN tf_bridge USING (tid) WHERE fid IS NULL)")
        
    ##
    # fetch the content from DB
    # return a list of informations for testing          
    def fetchNoteName(self):
        self.cur.execute("SELECT filename, ctag FROM head JOIN ctf_bridge USING (fid) JOIN ctag USING (ctid)")
        return self.cur.fetchall()
          
##
# \fn main()
# for testing
def main():
    #a = Note("./","rules.md")
    #s = a.forDB()

    a=NoteDB("test.db")
    a.updateDB("./")
    a.cleanTag()
    s = a.fetchNoteName()
    for i in s:
        print i[0],i[1]

        
if __name__=="__main__":
    main()

