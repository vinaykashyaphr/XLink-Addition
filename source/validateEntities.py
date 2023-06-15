def valent(XML, dirpath):
    import pathlib, os, re, sys
    import pandas as pd
    import tkinter as tk
    from tkinter import messagebox

    tk.Tk().withdraw()
    entpath = r"C:\catalog\ents\ent.xlsx" #getting reference excel files for entities
    dirpathPure0 = pathlib.PureWindowsPath(r'%s' %entpath) # converting to pure windows path
    entxl = dirpathPure0.as_posix()
    df = pd.read_excel(entxl) # reading reference excel
    listsrc = list(df['Entity']) # converting "Entity" column to list
    listrepl = list(df['Value']) # converting "Value" column to list
    listdict = {} #preparing a dictonary as Entity: Value
    [listdict.update({listsrc[i]:listrepl[i]}) for i in range(len(listsrc))]
        
    os.chdir(dirpath) # changing wd to local folder
    entver = open(XML, 'r', encoding='ISO-8859-1') # opening dmc as read by encoding to ISO-8859-1
    enttar = entver.read() # converting dmc to string
    entc = re.compile(r'(\&)(\w+)(\;)') # compiling for &word; format
    entl = entc.findall(enttar) # finding compilation inside string
    entver.close() # cloasing the read file

    for n in entl:
        ent = n[1] # getting only word except "&" and ";"
        for i, src in enumerate(listsrc): # looping through "Entity" column in excel
            if str(ent) == str(src): # comparing for matched entity in dmc
                enttar = enttar.replace("&{};".format(listsrc[i]), "&#{};".format(listrepl[i])) # replacing word in entity with value
                with open(str(XML), 'w', encoding='ISO-8859-1') as entitwr: # opening dmc to write by encoding to ISO-8859-1
                    entitwr.write(enttar) # writing replaced value
                    entitwr.flush()
                    entitwr.close() # closing the wrote file
            else:
                if any(listsrc) == False: # comparing for non matched entity in dmc
                    print("{} not found".format(ent))
                    messagebox.showerror("INVALID EXTERNAL ENTITY", 'Entity "{0}" not found\nAdd the entity "&{1};" in "ents.txt" and "ent.xlsx"'.format(ent, ent))
                    sys.exit(1)
    return XML # returning the xml file to continue the process