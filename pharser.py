#coding=utf-8
''' python library processing code

JSON data structure

- object - 
{
"Author": xxx,
"Date_create": xxx,
"Date_change": xxx,
"tags": [xxx,xxx,xxx],
"ctags": [xxx,xxx,xxx],
"content": xxx
}
'''

from os.path import isfile
from sys import exit
import re

NEWLINE = '\n'

def warning(line):
    """print warning context in red
    
    Args:
    line (str): content want to print
    """
    cWARNING = '\033[31m'
    ENDC = '\033[0m'
    print cWARNING+line+ENDC
    
class Note:
    """ Python class to store the content of one markdown file.

    """
    def __init__(self,filename):
        """An initialization code

        Args:
           filename (str): the name of a file to load-in
        """
        try:
            #### load file content
            if not isfile(filename):
                raise Exception("!! Fail to open %s !!"%filename)
            #### initial empty content
            self.filename = filename
            self.author = "EMPTY"
            self.dateChange = "EMPTY"
            self.date = "EMPTY"
            self.tags = []
            self.ctags = []
            self.content = ''
            
            with open(filename,'r') as f:
                fulltext = f.readlines()
            ### phrase content 
            if fulltext[0].strip(NEWLINE) != "<!--":
                raise Exception("!! Fail to recognize header as \n %s"
                                %fulltext[0].strip(NEWLINE))
            finishFlag = False
            for ii,line in enumerate(fulltext[1:]):
                if (line.strip(NEWLINE) == "-->"):
                    finishFlag = ii
                    break
                ## Start pumping header
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
                        self.populateHeaderObj(currentName,line[ia+1:])
                    else:
                        currentName = line[1:ib]
                        self.populateHeaderObj(currentName,line[ib+3:])
                elif currentName != '': # continue previous header
                    self.populateHeaderObj(currentName,line)
                else:  # unrecognized case
                    pass
            if not finishFlag:
                raise Exception("!! Unfinished header !!")
            ## load content
            if len(fulltext) == ii+2:
                raise Exception("!! Empty Content !!")
            self.content = "".join(fulltext[ii+2:])
        except Exception as inst:
            warning(inst.args[0])
            exit(1)

    def populateHeaderObj(self,name,content):
        """Populate the header content into Note class
        """
        content = content.strip() # remove leading and trailing spaces
        if name.lower() == "author": 
            self.author = content
        if name.lower() == "date created":
            self.dateCreate = content
        if name.lower() == "date changed":
            self.dateChange = content
        if name.lower() == "tags":
            self.populateTagArray(content)
        if name.lower() == "标签":
            self.populateTagArrayS(content)

    def populateTagArray(self,content):
        """Populate the header tag array, work only for or ";"
        """
        self.tags = re.split(';+', content)
        self.tags = [x.strip().capitalize() for x in self.tags if x]

    def populateTagArrayS(self,content):
        """Populate the header tag array, work only for "；" or ";"
        Mainly for Chinese 标签
        """
        self.ctags = re.split(';+|；+', content)
        self.ctags = [x.strip().capitalize() for x in self.ctags if x]

    def returnHeader(self):
        """Return header informaiton as string
        """
        str = "<!--\n" + \
            "+Author: %s\n"%self.author + \
            "+Date Created: %s\n"%self.dateCreate + \
            "+Date Changed: %s\n"%self.dateChange + \
            "+Tags: %s\n"%";".join(self.tags) + \
            "+标签: %s\n"%";".join(self.ctags) + \
            "-->\n"
        return str

    def writeFile(self,filename):
        """print to file
        """
        try:
            if isfile(filename):
                raise Exception("!! File (%s)Exist; Stop to overwrite !!"%filename)
            with open(filename,'w') as f:
                f.write(self.returnHeader()+content
        except Exception as inst:
            warning(inst.args[0])
            exit(1)
        
def loadfile(filename):
    '''convert file into JSON structure
    '''
    pass
    
def insertDB():
    '''insert data into database
    '''
    pass

def main():
    ''' main code 
    '''
    a = Note("rules.md")
    print a.returnHeader()+a.content
    
if __name__=="__main__":
    main()
