#coding=utf-8
## @package pharser
#  
#  \brief NoteOrganizer the file header
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
#  ### Database entry
#  
#  *table* 

from os.path import isfile
from sys import exit
import sqlite3 as sql
import glob
import re

from systools import *

##
#  \brief Class for markdown file note
#  \details This class build to load the file into program and support multiple output formats
#  \date 2014-01-17
class Note:
    ##
    # \brief Initialization code
    # \param filename name string of a file to load-in
    # \param fulltext if set, then create the Note from input text
    def __init__(self,filename,fulltext=[]):
        try:
            ## Filename of the Note 
            self.filename = filename
            if len(fulltext) == 0: # create new Note from file
                # !!! Exam file existency !!! #
                if not isfile(filename):
                    raise Exception("!! Fail to open %s !!"%filename)
                # !!! initial empty content !!! #
                ## Author of the Note 
                self.author = "EMPTY"
                ## Create Date of the Note
                self.dateCreate = "EMPTY"
                ## Create Date of the Note
                self.dateChange = "EMPTY"
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
            raise Exception("NoteClass","!!Fail to initialize %s"%self.filename)
    ##
    # \brief phrase the whole content
    def phraseContent(self,fulltext):
        if fulltext[0].strip(NEWLINE) != "<!--":
            raise Exception("!! Fail to recognize header as \n %s"
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
        self.content = "".join(fulltext[ii+2:])
        
    ##
    # \brief Populate the header content into Note class
    # \param name the keyword
    # \param content string contains all keywords
    def __populateHeaderObj(self,name,content):
        content = content.strip() # remove leading and trailing spaces
        if name.lower() == "author": 
            self.author = content
        if name.lower() == "date created":
            self.dateCreate = content
        if name.lower() == "date changed":
            self.dateChange = content
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
        self.tags = [x.strip().capitalize() for x in self.tags if x]
        return
    
    ##
    # \brief Populate the header ctags array, work only for or ";" and "；" 中文标签
    # \param content a ;-seperated list of tags
    #  Populate the header tag array, work only for  or ";"
    def __populateTagArrayS(self,content):
        self.ctags = re.split(';+|；+', content)
        self.ctags = [x.strip().capitalize() for x in self.ctags if x]
        return 
    ##
    # \brief return header information in one string
    def returnHeader(self):
        str = "<!--\n" + \
            "+Author: %s"%self.author + NEWLINE + \
            "+Date Created: %s"%self.dateCreate + NEWLINE + \
            "+Date Changed: %s"%self.dateChange + NEWLINE + \
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
                f.write(self.returnHeader()+content)
        except Exception as inst:
            warning(inst.args[0])
            exit(1)
        return
    ##
    # \fn forDB()
    # \brief return the tuple for database input
    def forDB(self):
        return (self.filename,'a','b','c','d','e','f')

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
class NoteDB():
    ## 
    # initialize the NoteDB class
    #  \param filename file name of the database
    #    if file exist, then read the database, otherwise ask to create one
    def __init__(self,filename):
        if isfile(filename):
            ## SQL connector
            self.conn = sql.connect(filename)
            ## SQL cursor
            self.cur = self.conn.cursor() 
        else:
            s = raw_input(">> Create a database '%s'? [n]/y: "%filename)
            if s != 'y':
                exit(0)
            path = raw_input(">> Input the path of md files: ")
            self.__createDB(filename)
            self.extendDB(path)
    ##
    # create a empty database        
    # \param filename file name of the database
    # \todo add time stamp
    def __createDB(self,filename):
        self.conn = sql.connect(filename)
        c = self.conn.cursor()
        c.execute(''' CREATE TABLE noteDB
        (filename text PRIMARY KEY,
        author text,
        date_create text,
        date_change text,
        tags text,
        ctags text,
        content text
        )
        ''')
        self.conn.commit()
        self.cur = c

    ##
    # expend the current database by given path
    # \param path path to md files
    # \todo 中文支持
    # need to expend to full path
    def extendDB(self,path):
        files = glob.glob(path+"/*.md")
        for ifile in files:
            try:
                print "- Insert "+ifile
                inote = Note(ifile)
                self.cur.execute("INSERT INTO noteDB VALUES (?,?,?,?,?,?,?)",
                                 inote.forDB())
                self.conn.commit()
            except Exception as inst:
                if (len(inst.args) == 2) and (inst.args[0]=="NoteClass"): # read-in fail
                    warning(inst.args[1])
                else: # other problems
                    raise inst
    ##
    # fetch the content from DB            
    def fetchDB(self):
        self.cur.execute("SELECT * FROM noteDB")
        print self.cur.fetchall()
              
##
# \fn main()
# for testing
def main():
    #Note("test.md")
    a=NoteDB("test.db")
    #a.extendDB("./")
    a.fetchDB()
    a.conn.close()

if __name__=="__main__":
    main()

