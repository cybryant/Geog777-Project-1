'''
Geog777 Project 1, Fall 2022
Cherie Bryant
main.py - user interface to adjust k-value & test for relationships between well
nitrogen levels and cancer
'''

import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import DISABLED, NORMAL, ttk
from tkinter import filedialog
from tkinter import BOTH
import subprocess
from PIL import Image, ImageTk
import arcpyAnalysis as aa


##################################
# IDENTIFY WHERE LAYOUTS WERE STORED BY runAnalysis.py
##################################
imageFolder = r"C:\Users\cheri\Documents\geog777\Project1\Project1Files\images"


##################################
# DEFINE ROOT WINDOW
##################################
root = tk.Tk()
root.title('Geog777 - Project 1, Spring 2022')
#root.iconbitmap()
root['bg']='DarkSeaGreen'
root.geometry('1100x750')


##################################
# FUNCTIONS
##################################
def runArcPy(k):
    ''' runs the arcPy analysis'''

    # update state of start button text so user know works has begun
    StartButton.configure(text="Processing...")

    # make report variables global so they are available as arguments for view button commands
    global moranReport
    global olsReport

    # data paths for the analysis
    wells = "Project1/shapefiles/well_nitrate.shp"
    tracts = "Project1/shapefiles/cancer_tracts.shp"
    counties = "Project1/shapefiles/cancer_county.shp"

    # test if k is over 1
    try: 
        k = float(k)
        if k <=1:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Value - Must be over 1.")

    # call runArcpy functions, activate buttons & update status statements as the 
    # results become available
    lblIDW.configure(text="Step 1 of 3: Inverse Distance Weighting is in process...")
    idwResults = aa.idw(wells, counties, k)
    idwVwButton.configure(state=NORMAL)
    idwSvButton.configure(state=NORMAL)
    lblIDW.configure(text="Step 1 of 3: Inverse Distance Weighting is complete.")

    lblOLS.configure(text="Step 2 of 3: Ordinary Least Squares is in process...")
    zoneStatResults = aa.zonalStats(tracts, idwResults, k)
    olsResults = aa.ols(zoneStatResults, k)
    olsReport = f"{imageFolder}/olsReport_{k}.pdf"
    olsVwButton.configure(state=NORMAL)
    olsSvButton.configure(state=NORMAL)
    olsReportButton.configure(state=NORMAL)
    lblOLS.configure(text="Step 2 of 3: Ordinary Least Squares is complete.")

    lblMoran.configure(text="Step 3 of 3: Validate using Moran's I is in process...")
    moranReport = aa.morans(olsResults, k)
    moranVwButton.configure(state=NORMAL)
    lblMoran.configure(text="Step 3 of 3: Validate using Moran's I is complete.")

    # update state of start button to inform user analysis is finished
    StartButton.configure(text="DONE!")

def showResults(reportName, k):
    '''upon button click, updates the view frame to show analysis image results'''
    imagePath = f"{imageFolder}\{reportName}_{k}.png"
    resultImg = ImageTk.PhotoImage(Image.open(imagePath))  #create image object
    resultImgFrame.configure(image=resultImg)
    resultImgFrame.image = resultImg
    # resultImgFrame.grid(row=0, column=0, columnspan=4)

def saveImg(reportName, k):
    '''allows user to save result images to a file'''
    savePath = filedialog.asksaveasfilename(initialdir="/")
    imagePath = f"{imageFolder}\{reportName}_{k}.png"
    img = Image.open(imagePath)
    img.save(savePath)    

def openMoransReport(path):
    '''opens an html window to see the report'''
    if path:
        subprocess.Popen(path, shell=True)
    else:
        messagebox.showerror("Error loading Moran's I report", "There was an error loading the Moran's I report.")

def openOLSReport(path):
    '''opens the OLS report PDF in a new window'''
    if path:
        subprocess.Popen(path, shell=True)
    else:
        messagebox.showerror("Error loading OLS report", "There was an error loading the OLS report.")

def showWells():
    '''upon button click, resets the view frame with the intial wells image'''
    resultImgFrame.configure(image=wellsImg)
    resultImgFrame.image = wellsImg


##################################
# SETUP THE TKINTER LAYOUT
##################################
# define input and view frames
viewFrame = tk.LabelFrame(root, bg='DarkSlateBlue', width=900, height=750, padx=5, pady=5)
inputFrame = tk.Frame(root, bg='DarkSeaGreen')
viewFrame.grid(column=0, row=0)
inputFrame.grid(column=1, row=0, padx=(12,10), pady=10)

# set inital state of view frame with points and census tracts displayed
wellsImgPath = "Project1/Project1Files/points.jpg"
wellsImg = ImageTk.PhotoImage(Image.open(wellsImgPath))
resultImgFrame = tk.Label(viewFrame, image=wellsImg, width=600, height=700)
resultImgFrame.grid(row=0, column=0, columnspan=5)


##################################
# DEFINE THE THE INPUT FRAME ELEMENTS
##################################
# define introductory text
introText = "\n Recently a possible cancer risk in adults from nitrate (and nitrite) has emerged, but the magnitude of the risk is unknown. The Wisconsin Department of Natural Resources has collected data on cancers by cataloging the location of all cancer occurrences over a ten-year period. In addition, they assembled a database of nitrate levels in a group of test wells throughout the county. \n\n This application allows you to explore the relationship between nitrate and cancer by prducing a raster map of nitrate values using inverse distance weighting. Since there is no theory to say what the distance exponent k should be, the application allows you to test various k-values over 1. The application then uses regression to determine if nitrate concentrations are related cancer occurrences. \n"

# create label to hold & display text
lblIntro = tk.Label(inputFrame, text=introText, wraplength=450, padx=5, bg="HoneyDew", borderwidth=1)
lblIntro.grid(row=0, column=0, columnspan=2)

# define text entry box & assign the value entered to a variable
lblEntry = tk.Label(inputFrame, text="Enter a value over 1:", bg='DarkSeaGreen', )
lblEntry.grid(row=1, column=0, sticky="E", pady=(75, 10))
kEntry = tk.Entry(inputFrame, width=20)
kEntry.grid(row=1, column=1, padx=10, pady=(75, 10), sticky="w")

# define button for user to submit k value
StartButton = tk.Button(inputFrame, text='Submit k-value', command=lambda: runArcPy(kEntry.get()))
StartButton.grid(row=2, column=0, columnspan=2, padx=5, pady=(10, 30))


##################################
# MAKE LABEL FRAME TO HOLD FEEDBACK MESSAGES
##################################
# create frame
feedbkFrame = tk.LabelFrame(inputFrame, bg="HoneyDew", width=200, text = "Status")
feedbkFrame.grid(row=3, column=0, columnspan=2)

# label for updating the user on the IDW process
lblIDW = tk.Label(feedbkFrame, text="Step 1 of 3: Inverse Distance Weighting has not yet started", bg="HoneyDew")
lblIDW.grid(row=0, column=0)

# label for updating the user on the OLS process
lblOLS = tk.Label(feedbkFrame, text="Step 2 of 3: Ordinary Least Squares has not yet started", bg="HoneyDew")
lblOLS.grid(row=1, column=0)

# label for updating the user on the Moran's process
lblMoran = tk.Label(feedbkFrame, text="Step 3 of 3: Validation using Moran's I has not yet started", bg="HoneyDew")
lblMoran.grid(row=2, column=0)


##################################
# DEFINE "SAVE" BUTTONS & SET INITIAL STATES TO DISABLED
##################################
# idw save button
idwSvButton = tk.Button(inputFrame, text='Save IDW Results as PNG', command=lambda: saveImg("IDW", kEntry.get()), state=DISABLED)
idwSvButton.grid(row=4, column=0, padx=5, pady=(75, 5))

# ols save button
olsSvButton = tk.Button(inputFrame, text='Save OLS Results as PNG', command=lambda: saveImg("OLS", kEntry.get()), state=DISABLED)
olsSvButton.grid(row=4, column=1, padx=5, pady=(75, 5))


##################################
# DEFINE "VIEW" BUTTONS & SET INITIAL STATES TO DISABLED
##################################
# wells button
wellsButton = tk.Button(viewFrame, text='View well point data', command=lambda: showWells())
wellsButton.grid(row=2, column=0, padx=5, pady=5)

# idw view button
idwVwButton = tk.Button(viewFrame, text='View IDW Results', command=lambda: showResults("IDW", kEntry.get()), state=DISABLED)
idwVwButton.grid(row=2, column=1, padx=5, pady=5)

# ols view button
olsVwButton = tk.Button(viewFrame, text='View OLS Results', command=lambda: showResults("OLS", kEntry.get()), state=DISABLED)
olsVwButton.grid(row=2, column=2, padx=5, pady=5)

# ols report button
olsReportButton = tk.Button(viewFrame, text='Open OLS Report', command=lambda: openOLSReport(olsReport), state=DISABLED)
olsReportButton.grid(row=2, column=3, padx=5, pady=5)

# moran report button
moranVwButton = tk.Button(viewFrame, text="Open Moran's I report", command=lambda: openMoransReport(moranReport), state=DISABLED)
moranVwButton.grid(row=2, column=4, padx=5, pady=5)


##################################
# RUN ROOT WINDOW MAIN LOOP
##################################
root.mainloop()
