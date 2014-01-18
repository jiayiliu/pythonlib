#coding=utf-8
## @package pharser
#  python library processing code
#
#  JSON data structure
# 
#  - object - 
#  {
#  "Author": xxx,
#  "Date_create": xxx,
#  "Date_change": xxx,
#  "tags": [xxx,xxx,xxx],
#  "ctags": [xxx,xxx,xxx],
#  "content": xxx
#  }


from os.path import isfile
from sys import exit
import re

## Newline symbol for Linux system
NEWLINE = '\n'

## \fn void warning(message)
#  \brief Create warning message in red
#  \param message a string of warning message
def warning(message):
    ## Define warning color
    cWARNING = '\033[31m'
    ## Define Normal color
    ENDC = '\033[0m'
    print cWARNING+message+ENDC

##
#  \brief Class for markdown file note
#  \details This class build to load the file into program and support multiple output formats
#  \author Jiayi Liu
#  \date 2014-01-17
#
class Note:
    ##
    # \fn Note __init__(filename)
    # \brief Initialization code
    # \param filename name string of a file to load-in
    def __init__(self,filename):
        try:
            # !!! Exam file existency !!! #
            if not isfile(filename):
                raise Exception("!! Fail to open %s !!"%filename)
            # !!! initial empty content !!! #
            ## Filename of the Note 
            self.filename = filename
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
            # !!! phrasing content !!! #
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
        except Exception as inst:
            warning(inst.args[0])
            exit(1)

    ##
    # \fn populateHeaderObj(name,content)
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
    # \fn populateTagArray(content)
    # \brief Populate the header tags array, work only for or ";"
    # \param content a ;-seperated list of tags
    def __populateTagArray(self,content):
        self.tags = re.split(';+', content)
        self.tags = [x.strip().capitalize() for x in self.tags if x]
        return
    
    ##
    # \fn populateTagArrayS(content)
    # \brief Populate the header ctags array, work only for or ";" and "；" 中文标签
    # \param content a ;-seperated list of tags
    #  Populate the header tag array, work only for  or ";"
    def __populateTagArrayS(self,content):
        self.ctags = re.split(';+|；+', content)
        self.ctags = [x.strip().capitalize() for x in self.ctags if x]
        return 
    ##
    # \fn str returnHeader()
    # \brief return header information in one string
    def returnHeader(self):
        str = "<!--\n" + \
            "+Author: %s\n"%self.author + \
            "+Date Created: %s\n"%self.dateCreate + \
            "+Date Changed: %s\n"%self.dateChange + \
            "+Tags: %s\n"%";".join(self.tags) + \
            "+标签: %s\n"%";".join(self.ctags) + \
            "-->\n"
        return str

    ##
    # \fn writeFile(filename)
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
# \fn main()
# for testing
def main():
    a = Note("rules.md")
    print a.returnHeader()+a.content

if __name__=="__main__":
    main()

