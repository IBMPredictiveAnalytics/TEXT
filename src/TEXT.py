# extension module
#/***********************************************************************
# * Licensed Materials - Property of IBM 
# *
# * IBM SPSS Products: Statistics Common
# *
# * (C) Copyright IBM Corp. 1989, 2020
# *
# * US Government Users Restricted Rights - Use, duplication or disclosure
# * restricted by GSA ADP Schedule Contract with IBM Corp. 
# ************************************************************************/

from extension import Template, Syntax
import spss
import time, getpass, textwrap


__version__ = "1.4.0"
__author__ = "JKP"

# history
# 21-dec-2009 enable localization
# 01-sep-2010 add substitution support
# 03-dec-2013 Handle extraneous +/- characters that appear, WRAP parameter

    
helptext="""Create a text block in the Viewer, optionally with formatted text

TEXT list-of-strings
[/OUTLINE [HEADING=text] [TITLE=text] [PAGEBREAK={NO*|YES}]
[/WRAP WRAP=number]
[/HELP]

Example:
TEXT 'The following analysis assumes normally distributed residuals'
'If this assumption is false, confidence intervals may be incorrect.'
/OUTLINE HEADING="Attention" TITLE='Note to Reader'.

The text is inserted in a new textblock in the Viewer.  Each quoted string is
a single line.  If no strings are supplied, an empty comment will be created.
There must be a nonempty dataset open before this command can be used.

Literal concatenation using the standard SPSS convention of "+" can be
used, but a "-" can be used for the same purpose (quotes are not
necessary).  Using a - allows any number of lines to be combined.

If the text appears to be html or rtf, it is inserted as formatted 
text in the Viewer if running Version 17 or later and in local mode.
(Newer versions of Statistics may support this functionality in
distributed mode.)  In this case, all the lines are joined without 
any separator, so the line distinction in the quoted strings does not apply.

The symbol )USER in the text is replaced with the current user name.
The symbol )CURDATE is replaced with the current date and time.

The text appears under the Outline heading specified in HEADING.  
The default heading is "Comment"  The specified title appears as 
the text label in the outline.  HEADING and TITLE text should be 
enclosed in quotes.  It also defaults to "Comment" if inserting a
formatted text block.

If PAGEBREAK=YES, a page break is inserted before the text block.  
This feature is only available with Version 17 or later running 
in local mode.  In version 16, PAGEBREAK is ignored.

If the text is not html or rtf, WRAP can specify the maximum number
of characters on a line.  Longer lines will be wrapped at an appropriate
blank, but if some text has no possible wrap points, it will be allowed
to be longer.

/HELP displays this text and does nothing else."""

def Run(args):
    """Execute the TEXT command"""


    args = args[list(args.keys())[0]]
    ###print args


    # define the TEXT subcommand syntax
    oobj = Syntax([
        Template("", subc="", var="strings", ktype="literal", islist=True),
        
        Template("HEADING", subc="OUTLINE", var="heading", ktype="literal"),
        Template("TITLE", subc="OUTLINE", var="otitle", ktype="literal"),
        Template("PAGEBREAK", subc="OUTLINE", var="pagebreak", ktype="bool"),
        
        Template("WRAP", subc="WRAP", var="wrap", ktype="int", vallist=[1]),
    ])
    
    # ensure localization function is defined
    global _
    try:
        _("---")
    except:
        def _(msg):
            return msg

    if "HELP" in args:
        #print helptext
        helper()
    else:
        oobj.parsecmd(args)
        createText(**oobj.parsedparams)

def createText(strings=[""], otitle="Comment", heading="Comment", pagebreak=False, wrap=None):
    """Create a textblock in the Viewer with contents strings.

    strings is a sequence of lines of text to insert in the block.  If omitted,
    the block will be empty.
    otitle is an optional title to appear in the outline.
    heading is the procedure name that will appear first in the outline and the associated item on the right.
    If pagebreak is True and this is version 17 or later, a pagebreak is inserted.
    If the text appears to be html or rtf, it is inserted with formatting (using a scripting api) if 17 or later
    """
    # debugging
    # makes debug apply only to the current thread
    #try:
        #import wingdbstub
        #if wingdbstub.debugger != None:
            #import time
            #wingdbstub.debugger.StopDebug()
            #time.sleep(1)
            #wingdbstub.debugger.StartDebug()
        #import thread
        #wingdbstub.debugger.SetDebugThreads({thread.get_ident(): 1}, default_policy=0)
        ## for V19 use
        ###    ###SpssClient._heartBeat(False)
    #except:
        #pass
    try:
        spss.StartProcedure(heading)
    except:
        raise ValueError(_("Error: There must be a nonempty active dataset before using this command."))
    user = getpass.getuser()
    curdate = time.asctime()
    for i in range(len(strings)):
        strings[i] = strings[i].replace(")USER", user)
        strings[i] = strings[i].replace(")CURDATE", curdate)
    start = strings[0][:7].lower()
    # The rtf code below screams for an r prefix, but the start text is coming through non-raw
    if not (start.startswith("<html>") or start.startswith("{\rtf")) or spss.GetDefaultPlugInVersion()[4:] < "170":
        strings, nitems = reducer(strings)
        if not wrap is None:
            strings = "\n".join(textwrap.wrap(strings, width=wrap, 
                break_long_words=False))
        t = spss.TextBlock(otitle, strings)
        # lines are appended at once for better performance
        spss.EndProcedure()
    else:
        spss.TextBlock(otitle, "")
        spss.EndProcedure()
        
        # do the rest with scripting apis
        
        import SpssClient
        SpssClient.StartClient()
        time.sleep(.1)       # text block should have arrived in Viewer, but pause briefly
        odoc = SpssClient.GetDesignatedOutputDoc()
        items = odoc.GetOutputItems()
        # Allow for some delay in the text block getting into the Viewer
        for i in range(5):
            size = items.Size()
            item = items.GetItemAt(size-1)
            if item.GetType() == SpssClient.OutputItemType.TEXT:
                break
            time.sleep(.5)
        specificitem = item.GetSpecificType()
        specificitem.SetTextContents("".join(strings))
        item.SetDescription(otitle)
        items.GetItemAt(size-2).SetVisible(False)
        if pagebreak:
            item.SetPageBreak(True)
        SpssClient.StopClient()
        return

    if pagebreak and spss.GetDefaultPlugInVersion()[4:] >= '170':
        import SpssClient
        try:
            SpssClient.StartClient()
            items = SpssClient.GetDesignatedOutputDoc().GetOutputItems()
            item = items.GetItemAt(items.Size()-1)
            item.SetPageBreak(True)
            SpssClient.StopClient()
        except:   # do not propagate
            SpssClient.StopClient()
            
def reducer(s):
    """Return wrapped string and linecount where +/- items are concatenated 
    with blank and others with newline"""
    
    ss = [s[0]]
    try:
        for i in range(1, len(s)):
            if s[i] == "+" or s[i] == "-":
                ss[-1] = ss[-1] + " " + (s[i+1])
                s[i+1] = None
            elif not s[i] is None:
                ss.append(s[i])
    except:
        pass
    return "\n".join(ss), len(ss)

def helper():
    """open html help in default browser window
    
    The location is computed from the current module name"""
    
    import webbrowser, os.path
    
    path = os.path.splitext(__file__)[0]
    helpspec = "file://" + path + os.path.sep + \
         "markdown.html"
    
    # webbrowser.open seems not to work well
    browser = webbrowser.get()
    if not browser.open_new(helpspec):
        print(("Help file not found:" + helpspec))
try:    #override
    from extension import helper
except:
    pass    