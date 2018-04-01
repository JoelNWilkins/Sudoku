import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
from tkinter.colorchooser import askcolor
from tkinter import font

import os
import sys
import shutil
import subprocess
import csv
import pickle
import time
import math
from copy import deepcopy
from collections import Counter

import solver

appData = os.getenv("LOCALAPPDATA")

#sys.stdout = open(appData+"\\Sudoku\\Sudoku.txt", "w")
#sys.stderr = open(appData+"\\Sudoku\\Sudoku.txt", "w")

if not "Sudoku" in os.listdir(appData):
    os.makedirs(appData+"\\Sudoku\\")

if not "Puzzles" in os.listdir(appData+"\\Sudoku\\"):
    shutil.copytree(os.getcwd()+"\\Puzzles", appData+"\\Sudoku\\Puzzles")
    
if (not "programData.pkl" in os.listdir(appData+"\\Sudoku\\")
    or os.path.getsize(appData+"\\Sudoku\\programData.pkl") == 0):
    data = {"filename": appData+"\\Sudoku\\Puzzles\\Easy\\Easy 1.puz",
            "timer": True, "position": True, "location": os.getcwd(),
            "style": {"size": 19, "width": 1, "colour": "#000000",
                      "error": "#FF0000", "line": "#000000",
                      "start": "#000000"}}
    
    pickle.dump(data, open(appData+"\\Sudoku\\programData.pkl", "wb"))

try:
    data = pickle.load(open(appData+"\\Sudoku\\programData.pkl", "rb"))
    os.chdir(data["location"])
    location = data["location"]
except:
    location = os.getcwd()

DETACHED_PROCESS = 0x00000008
if subprocess.call("assoc .puz", creationflags=DETACHED_PROCESS, shell=True):
    subprocess.call("assoc .puz=puz_file", creationflags=DETACHED_PROCESS,
                    shell=True)
    subprocess.call("ftype puz_file=\"{}\\Sudoku.exe %1\""
                    .format(location), creationflags=DETACHED_PROCESS,
                    shell=True)

class Sudoku(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self)
        self.title("Sudoku")
        self.iconbitmap(default="Files\\logo.ico")

        self.protocol("WM_DELETE_WINDOW", self.closeWindow)

        self.resizable(False, False)

        self.timerVar = tk.BooleanVar()
        self.positionVar = tk.BooleanVar()
        self.errorVar = tk.BooleanVar()

        self.timerVar.set(True)
        self.positionVar.set(True)
        self.errorVar.set(True)

        self.style = {"size": 19, "width": 1, "colour": "#000000",
                      "error": "#FF0000", "line": "#000000", "start": "#000000"}

        if "directory" in kwargs.keys():
            self.directory = kwargs["directory"]
        else:
            self.directory = os.getcwd()

        fileName = None
        if "fileName" in kwargs.keys():
            fileName = kwargs["fileName"]
        if fileName == None:
            fileName = self.loadData()

        self.timerLabel = "Play / Pause"

        self.menuBar = MenuBar(self)

        self.gridFrame = GridFrame(self)
        self.gridFrame.pack(fill="both", expand=True)

        size = int(self.gridFrame.getSize()/2) - 2
        if size < 8:
            size = 8

        self.statusBar = StatusBar(self, command=self.timerStatus, size=size)
        self.statusBar.pack(side="bottom", fill="x", expand=True)

        if self.statusBar.getStatus() == "play":
            self.timerLabel = "Pause"
        else:
            self.timerLabel = "Play"

        try: 
            self.openFile(fileName=fileName)
        except IndexError:
            self.title("Untitled - Sudoku")

    def newFile(self, *args, **kwargs):
        self.gridFrame.newFile(*args, **kwargs)
        
        self.statusBar.reset()

    def openFile(self, *args, **kwargs):
        self.statusBar.pause()
        
        minutes, seconds = self.gridFrame.openFile(*args, **kwargs)

        total = (60 * minutes) + seconds

        self.statusBar.reset()
        self.statusBar.setTime(minutes, seconds)

        if not self.gridFrame.check():
            self.statusBar.play()
        else:
            self.statusBar.pause()

        self.statusBar.redraw()

    def saveFile(self, *args, **kwargs):
        minutes, seconds = self.statusBar.getTime()
        status = self.statusBar.getStatus()
        self.statusBar.pause()
        
        self.gridFrame.saveAsFile(*args, minutes=minutes, seconds=seconds,
                                  fileName=self.fileName, **kwargs)

        if status == "play":
            self.statusBar.play()

    def saveAsFile(self, *args, **kwargs):
        minutes, seconds = self.statusBar.getTime()
        status = self.statusBar.getStatus()
        self.statusBar.pause()
        
        self.gridFrame.saveAsFile(*args, minutes=minutes, seconds=seconds,
                                  **kwargs)

        if status == "play":
            self.statusBar.play()

    def createSudoku(self, *args, **kwargs):
        self.gridFrame.createSudoku(*args, **kwargs)
        
        self.statusBar.reset()
        self.statusBar.play()

    def closeWindow(self, *args, **kwargs):
        self.saveData()
            
        if self.gridFrame.modified():
            save = messagebox.askyesnocancel("Save?",
                "This file has been modified. Do you want to save the changes?")

            if save != None:
                if save:
                    self.saveAsFile()
                self.destroy()
        else:
            self.destroy()

    def saveData(self, *args, **kwargs):
        if "fileName" in kwargs.keys():
            fileName = kwargs["fileName"]
        else:
            fileName = self.fileName
            
        data = {"filename": fileName, "timer": self.timerVar.get(),
                "position": self.positionVar.get(), "style": self.style,
                "error": self.errorVar.get(), "location": os.getcwd()}
        
        pickle.dump(data, open(self.directory+"\\programData.pkl", "wb"))

    def loadData(self, *args, **kwargs):
        data = pickle.load(open(self.directory+"\\programData.pkl", "rb"))

        try:
            fileName = data["filename"]
        except:
            pass

        try:
            self.timerVar.set(data["timer"])
        except:
            pass

        try:
            self.style = data["style"]
        except:
            pass

        try:
            self.positionVar.set(data["position"])
        except:
            pass

        try:
            self.errorVar.set(data["error"])
        except:
            pass

        try:
            self.updateStatus()
        except:
            pass

        return fileName

    def reset(self, *args, **kwargs):
        resetSudoku = messagebox.askyesnocancel("Reset?",
"""Are you sure you want to reset this puzzle?
This action cannot be undone.""")

        if resetSudoku:
            self.gridFrame.grid = deepcopy(self.gridFrame.start)
            
            self.gridFrame.possible = []
            for r in range(9):
                self.gridFrame.possible.append([])
                for c in range(9):
                    self.gridFrame.possible[r].append([])

            self.gridFrame.updateGrid()
            self.statusBar.reset()

    def check(self, *args, **kwargs):
        if self.gridFrame.check():
            minutes, seconds = self.statusBar.pause()

            if self.timerVar.get():
                save = messagebox.askyesnocancel("Congratulations!",
"""Congratulations!
You have completed the sudoku in {} minutes and {} seconds.
Do you want to save your solution?""".format(minutes, seconds))
            else:
                save = messagebox.askyesnocancel("Congratulations!",
"""Congratulations!
You have completed the sudoku.
Do you want to save your solution?""".format(minutes, seconds))

            if save != None:
                if save:
                    self.saveAsFile(fileName=self.fileName)
                self.statusBar.pause()
        else:
            messagebox.showinfo("Not quite.",
"Not quite. There is an error in your solution.")

    def solve(self, *args, **kwargs):
        self.statusBar.pause()
        
        s = solver.Solver(self.gridFrame.start)

        start = time.time()
        
        (self.gridFrame.start, self.gridFrame.grid,
         self.gridFrame.possible) = s.solve()

        elapsed = time.time() - start
        
        self.gridFrame.updateGrid()

        if s.check() and self.timerVar.get():
            if int(math.floor(elapsed)) == 0:
                timeTaken = "{} milliseconds".format(int(round(elapsed * 1000)))
            else:
                timeTaken = ("{} seconds and {} milliseconds"
                .format(int(math.floor(elapsed)), int(round(elapsed * 1000))))
            messagebox.showinfo("Solved",
"The sudoku was solved in {}.".format(timeTaken))

        pos = self.gridFrame.position.get()
        self.gridFrame.cells[int(pos[0])][int(pos[1])].invoke()

    def toggle(self, *args, **kwargs):
        self.statusBar.toggle()

    def setTime(self, minutes, seconds, *args, **kwargs):
        self.statusBar.setTime(minutes, seconds)

    def getTime(self, *args, **kwargs):
        return self.statusBar.getTime()

    def resize(self, *args, **kwargs):
        start = self.gridFrame.start
        grid = self.gridFrame.grid
        possible = self.gridFrame.possible
        position = self.gridFrame.position.get()
        title = self.title()
        fileName = self.fileName

        self.gridFrame.pack_forget()
        self.gridFrame = GridFrame(self)
        self.gridFrame.pack(fill="both", expand=True)

        self.gridFrame.start = start
        self.gridFrame.grid = grid
        self.gridFrame.possible = possible
        self.gridFrame.position.set(position)
        self.title(title)
        self.fileName = fileName

        self.gridFrame.updateGrid()
        self.gridFrame.cells[int(position[0])][int(position[1])].invoke()

        size = int(self.gridFrame.getSize()/2) - 2
        if size < 8:
            size = 8

        self.statusBar.setSize(size)

    def updatePos(self, *args, **kwargs):
        self.statusBar.updatePos()

    def updateErrors(self, *args, **kwargs):
        self.gridFrame.updateErrors()

    def updateStatus(self, *args, **kwargs):
        self.statusBar.updateStatus()

        if self.timerVar.get() or self.positionVar.get():
            self.statusBar.pack(side="bottom", fill="x", expand=True)
        else:
            self.statusBar.pack_forget()

    def timerStatus(self, *args, **kwargs):
        if self.statusBar.getStatus() == "play":
            self.timerLabel = "Pause"
        else:
            self.timerLabel = "Play"
            
        self.menuBar.editMenu.entryconfig(0, label=str(self.timerLabel))

class GridFrame(tk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, *args, master=parent, **kwargs)

        self.lineColour = self.master.style["line"]
        self.activeColour = "white"
        self.lineRelief = "solid"

        width = int(self.master.style["width"])

        self.frame = tk.Frame(self, relief=self.lineRelief,
                              highlightthickness=int(1.5 * width) + 1,
                              highlightbackground=self.lineColour,
                              highlightcolor=self.lineColour)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.normalFont = font.Font(family="Courier", weight="normal",
                                    size=self.master.style["size"])
        self.boldFont = font.Font(family=self.normalFont["family"],
                                  size=self.normalFont["size"], weight="bold")
        self.smallFont = font.Font(family=self.normalFont["family"],
                                   size=int((self.normalFont["size"] - 1) / 3))

        if self.normalFont["size"] > 22:
            self.smallFont["size"] -= 1
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
    
        for n in range(9):
            self.frame.rowconfigure(n+n//3, weight=1)
            self.frame.columnconfigure(n+n//3, weight=1)
        
        self.position = tk.StringVar()
        self.position.set("00")

        self.newFile()

        self.master.unbind("<Key>")
        self.master.unbind("<Button-1>")
        self.master.unbind("<Up>")
        self.master.unbind("<Down>")
        self.master.unbind("<Left>")
        self.master.unbind("<Right>")
        self.master.unbind("<BackSpace>")

        self.master.bind("<Key>", self.keyPressed)
        self.master.bind("<Button-1>", self.callback)
        self.master.bind("<Up>", self.upKey)
        self.master.bind("<Down>", self.downKey)
        self.master.bind("<Left>", self.leftKey)
        self.master.bind("<Right>", self.rightKey)
        self.master.bind("<BackSpace>", self.backSpaceKey)

    def updateGrid(self, *args, **kwargs):
        self.normalFont = font.Font(family="Courier", weight="normal",
                                    size=self.master.style["size"])
        self.boldFont = font.Font(family=self.normalFont["family"],
                                  size=self.normalFont["size"], weight="bold")
        self.smallFont = font.Font(family=self.normalFont["family"],
                                   size=int((self.normalFont["size"] - 1) / 3))

        if self.normalFont["size"] > 22:
            self.normalFont["size"] += 1

        self.lineColour = self.master.style["line"]
        width = int(self.master.style["width"])

        self.frame.config(highlightthickness=int(1.5 * width) + 1)

        self.line1 = tk.Frame(self.frame, borderwidth=0, relief=self.lineRelief,
                              background=self.lineColour, width=width)
        self.line1.grid(row=0, column=3, rowspan=11, sticky="nsew")
        self.line2 = tk.Frame(self.frame, borderwidth=0, relief=self.lineRelief,
                              background=self.lineColour, width=width)
        self.line2.grid(row=0, column=7, rowspan=11, sticky="nsew")
        self.line3 = tk.Frame(self.frame, borderwidth=0, relief=self.lineRelief,
                              background=self.lineColour, height=width)
        self.line3.grid(row=3, column=0, columnspan=11, sticky="nsew")
        self.line4 = tk.Frame(self.frame, borderwidth=0, relief=self.lineRelief,
                              background=self.lineColour, height=width)
        self.line4.grid(row=7, column=0, columnspan=11, sticky="nsew")
        
        self.cells = []
        for r in range(9):
            self.cells.append([])
            for c in range(9):
                if self.start[r][c] != 0:
                    fontStyle = self.boldFont
                else:
                    fontStyle = self.normalFont
                    
                self.cells[r].append(Cell(self.frame,
                                          variable=self.position,
                                          value=(str(r)+str(c)),
                                          command=self.updateCells,
                                          font=fontStyle, borderwidth=0,
                                          relief=self.lineRelief,
                                          highlightthickness=width,
                                          highlightbackground=self.lineColour,
                                          highlightcolor=self.lineColour,
                                          activebackground=self.activeColour,
                                          width=2, height=1, padx=3, pady=3))
                self.cells[r][c].grid(row=r+r//3, column=c+c//3, sticky="nsew")
                
                if self.grid[r][c] != 0:
                    self.cells[r][c].set(self.grid[r][c])
                elif self.possible[r][c] != []:
                    self.cells[r][c].possible(self.possible[r][c],
                                              font=self.smallFont)
                else:
                    self.cells[r][c].set(0)

        try:
            pos = self.position.get()
            self.cells[int(pos[0])][int(pos[1])].invoke()
        except:
            pass
                    
        self.updateErrors()

    def updateCells(self, *args, **kwargs):
        for row in self.cells:
            for cell in row:
                cell.update()

        self.master.updatePos()
        self.updateErrors()

    def changeSize(self, *args, **kwargs):
        self.config(width=0, height=0)
        self.frame.config(width=0, height=0)

    def callback(self, event):
        self.focus_set()

    def keyPressed(self, event):
        key = event.char
        shiftKeys = [')', '!', '"', '£', '$', '%', '^', '&', '*', '(']
        if key in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            key = int(event.char)
            pos = self.position.get()
            r = int(pos[0])
            c = int(pos[1])
            
            if self.start[r][c] == 0:
                self.grid[r][c] = key
                self.possible[r][c] = []

                self.cells[r][c].set(key)
        elif key in shiftKeys:
            key = shiftKeys.index(key)
            pos = self.position.get()
            r = int(pos[0])
            c = int(pos[1])
            
            if self.start[r][c] == 0 and self.grid[r][c] == 0:
                if key in self.possible[r][c]:
                    self.possible[r][c].remove(key)
                else:
                    self.possible[r][c].append(key)
                    
                self.cells[r][c].possible(self.possible[r][c],
                                          font=self.smallFont)
                self.cells[r][c].update()

        self.updateErrors()

    def upKey(self, event):
        pos = self.position.get()
        r = int(pos[0])
        c = int(pos[1])
        r -= 1
        if r < 0:
            r = 0
        self.cells[r][c].invoke()

    def downKey(self, event):
        pos = self.position.get()
        r = int(pos[0])
        c = int(pos[1])
        r += 1
        if r > 8:
            r = 8
        self.cells[r][c].invoke()

    def leftKey(self, event):
        pos = self.position.get()
        r = int(pos[0])
        c = int(pos[1])
        c -= 1
        if c < 0:
            c = 0
        self.cells[r][c].invoke()

    def rightKey(self, event):
        pos = self.position.get()
        r = int(pos[0])
        c = int(pos[1])
        c += 1
        if c > 8:
            c = 8
        self.cells[r][c].invoke()

    def backSpaceKey(self, event):
        pos = self.position.get()
        r = int(pos[0])
        c = int(pos[1])
        
        if self.start[r][c] == 0:
            self.grid[r][c] = 0
            self.possible[r][c] = []

            self.cells[r][c].set(0)

        self.updateErrors()

    def newFile(self, *args, **kwargs):
        self.start = []
        self.grid = []
        self.possible = []
        for r in range(9):
            self.start.append([])
            self.grid.append([])
            self.possible.append([])
            for c in range(9):
                self.start[r].append(0)
                self.grid[r].append(0)
                self.possible[r].append([])

        self.master.fileName = None
        self.master.title("Untitled - Sudoku")

        self.initialStart = deepcopy(self.start)
        self.initialGrid = deepcopy(self.grid)
        self.initialPossible = deepcopy(self.possible)

        self.updateGrid()

    def openFile(self, *args, **kwargs):
        oldFileName = self.master.fileName
        oldStart = deepcopy(self.start)
        oldGrid = deepcopy(self.grid)
        oldPossible = deepcopy(self.possible)

        minutes = 0
        seconds = 0

        fileName = None
        if "fileName" in kwargs.keys():
            fileName = kwargs["fileName"]
        if fileName == None:
            fileName = askopenfilename(parent=self.master,
                                       initialdir=self.master.directory
                                       + "\\Puzzles\\",
                                       filetypes=[("Puzzle Files", "*.puz")],
                                       defaultextension=".puz")

        try:
            self.newFile()
            
            with open(fileName, "r") as f:
                csvreader = csv.reader(f, delimiter=",")

                r = 0
                for row in csvreader:
                    if r < 9:
                        c = 0
                        for cell in row:
                            if "$" in cell:
                                self.start[r][c] = int(cell.replace("$", ""))
                                self.grid[r][c] = int(cell.replace("$", ""))
                            elif "?" in cell:
                                values = []
                                for item in list(cell.replace("?", "")):
                                    values.append(int(item))
                                self.possible[r][c] = values
                            else:
                                self.grid[r][c] = int(cell)
                            c += 1
                        r += 1
                    else:
                        try:
                            minutes = int(row[0])
                            seconds = int(row[1])
                        except:
                            minutes = 0
                            seconds = 0

            self.master.fileName = fileName
            if "\\" in fileName:
                self.master.title("{} - Sudoku".format(fileName.split("\\")[-1]
                                                       .replace(".puz", "")))
            else:
                self.master.title("{} - Sudoku".format(fileName.split("/")[-1]
                                                       .replace(".puz", "")))

            self.initialStart = deepcopy(self.start)
            self.initialGrid = deepcopy(self.grid)
            self.initialPossible = deepcopy(self.possible)

            self.master.saveData(fileName=fileName)
                
        except FileNotFoundError:
            if oldFileName != None:
                self.master.fileName = oldFileName
                if "\\" in oldFileName:
                    self.master.title("{} - Sudoku"
                                      .format(oldFileName.split("\\")[-1]
                                              .replace(".puz", "")))
                else:
                    self.master.title("{} - Sudoku"
                                      .format(oldFileName.split("/")[-1]
                                              .replace(".puz", "")))
                    
                self.start = deepcopy(oldStart)
                self.grid = deepcopy(oldGrid)
                self.possible = deepcopy(oldPossible)
            else:
                self.newFile()
        except:
            self.start = deepcopy(oldStart)
            self.grid = deepcopy(oldGrid)
            self.possible = deepcopy(oldPossible)

        self.updateGrid()
        return (minutes, seconds)

    def saveAsFile(self, *args, **kwargs):
        fileName = None
        if "fileName" in kwargs.keys():
            fileName = kwargs["fileName"]
        if fileName == None:
            fileName = asksaveasfilename(parent=self.master,
                                         initialdir=self.master.directory
                                         + "\\Puzzles\\",
                                         filetypes=[("Puzzle Files", "*.puz")],
                                         defaultextension=".puz")

        if "minutes" in kwargs.keys() and "seconds" in kwargs.keys():
            minutes = kwargs["minutes"]
            seconds = kwargs["seconds"]
        else:
            minutes = 0
            seconds = 0

        try:
            with open(fileName, "w", newline="") as f:
                csvwriter = csv.writer(f, delimiter=",")

                for r in range(9):
                    row = list(range(1, 10))
                    for c in range(9):
                        if self.start[r][c] != 0:
                            row[c] = "${}".format(self.start[r][c])
                        elif self.possible[r][c] != []:
                            possibilities = ""
                            for item in self.possible[r][c]:
                                possibilities += str(item)
                            row[c] = "?{}".format(possibilities)
                        else:
                            row[c] = self.grid[r][c]
                        
                    csvwriter.writerow(row)
                    
                    r += 1

                m, s = self.master.getTime()
                if minutes != 0 or seconds != 0:
                    csvwriter.writerow([minutes, seconds])
                else:
                    csvwriter.writerow([m, s])

            self.master.fileName = fileName
            if "\\" in fileName:
                self.master.title("{} - Sudoku".format(fileName.split("\\")[-1]
                                                       .replace(".puz", "")))
            else:
                self.master.title("{} - Sudoku".format(fileName.split("/")[-1]
                                                       .replace(".puz", "")))

            self.initialStart = deepcopy(self.start)
            self.initialGrid = deepcopy(self.grid)
            self.initialPossible = deepcopy(self.possible)

            self.master.saveData()
                
        except PermissionError:
            messagebox.showerror("Permission Error",
"Sudoku is unable to save to this file as it is open in another program.")
        except FileNotFoundError:
            pass

    def createSudoku(self, *args, **kwargs):
        fileName = asksaveasfilename(parent=self.master,
                                     initialdir=self.master.directory
                                     + "\\Puzzles\\",
                                     filetypes=[("Puzzle Files", "*.puz")],
                                     defaultextension=".puz")

        try:
            with open(fileName, "w", newline="") as f:
                csvwriter = csv.writer(f, delimiter=",")

                for row in self.grid:
                    for i in range(len(row)):
                        if row[i] != 0:
                            row[i] = "${}".format(row[i])
                        
                    csvwriter.writerow(row)

            self.openFile(fileName=fileName)
            
        except PermissionError:
            messagebox.showerror("Permission Error",
    "Sudoku is unable to save to this file as it is open in another program.")
        except FileNotFoundError:
            pass
        except:
            raise

    def check(self, *args, **kwargs):
        for i in range(9):
            row = self.checkRow(i)
            col = self.checkCol(i)
            box = self.checkBox(i)
            if not (row and col and box):
                return False
        return True

    def checkRow(self, i):
        if sorted(self.grid[i]) == list(range(1, 10)):
            return True
        else:
            return False

    def checkCol(self, i):
        col = self.getCol(i)
        if sorted(col) == list(range(1, 10)):
            return True
        else:
            return False

    def checkBox(self, i):
        box = self.getBox(i)
        if sorted(box) == list(range(1, 10)):
            return True
        else:
            return False

    def getCol(self, i):
        column = []
        for n in range(9):
            column.append(self.grid[n][i])
        return column

    def getBox(self, i):
        box = []
        for n in range(3):
            box.extend(self.grid[3*(i//3)+n][3*(i%3):3*(i%3)+3])
        return box

    def findErrors(self, *args, **kwargs):
        errors = []
        for i in range(9):
            row = self.grid[i]
            freq = Counter(row)
            count = 0
            for item in row:
                if freq[item] > 1:
                    errors.append([i, count])
                count += 1
                
            column = self.getCol(i)
            freq = Counter(column)
            count = 0
            for item in column:
                if freq[item] > 1:
                    errors.append([count, i])
                count += 1
                
            box = self.getBox(i)
            freq = Counter(box)
            count = 0
            for item in box:
                if freq[item] > 1:
                    errors.append([3*(i//3)+count//3, 3*(i%3)+count%3])
                count += 1
        return errors

    def updateErrors(self, *args, **kwargs):
        if self.master.errorVar.get():
            errors = self.findErrors()
        else:
            errors = []
            
        for row in range(9):
            for column in range(9):
                if self.start[row][column] != 0:
                    self.cells[row][column].config(
                        fg=self.master.style["start"])
                elif ([row, column] in errors and self.start[row][column] == 0
                    and self.grid[row][column] != 0):
                    self.cells[row][column].config(
                        fg=self.master.style["error"])
                else:
                    self.cells[row][column].config(
                        fg=self.master.style["colour"])

    def modified(self, *args, **kwargs):
        if self.initialStart != self.start:
            return True
        if self.initialGrid != self.grid:
            return True
        if self.initialPossible != self.possible:
            return True
        return False

    def getSize(self, *args, **kwargs):
        return self.normalFont["size"]

class Cell(tk.Radiobutton):
    def __init__(self, parent, *args, **kwargs):
        if "variable" in kwargs.keys():
            self.variable = kwargs.pop("variable")
        if "value" in kwargs.keys():
            self.value = kwargs.pop("value")
        if "command" in kwargs.keys():
            self.command = kwargs.pop("command")
        if "background" in kwargs.keys():
            self.background = kwargs.pop("background")
        elif "bg" in kwargs.keys():
            self.background = kwargs.pop("bg")
        else:
            self.background = parent.cget("bg")
        if "activebackground" in kwargs.keys():
            self.activebackground = kwargs.pop("activebackground")
        else:
            self.activebackground = self.background

        self.parent = tk.Frame(parent)

        if "highlightthickness" in kwargs.keys():
            bd = kwargs.pop("highlightthickness")
            self.parent.config(padx=bd, pady=bd)
        if "highlightcolor" in kwargs.keys():
            bg = kwargs.pop("highlightcolor")
            self.parent.config(bg=bg)
        if "highlightbackground" in kwargs.keys():
            bg = kwargs.pop("highlightbackground")
            self.parent.config(bg=bg)
            
        tk.Label.__init__(self, *args, master=self.parent, **kwargs)
        self.pack_configure(fill=tk.BOTH, expand=True)
        
        self.numbers = []

        self.bind("<Button-1>", self.press)

    def grid(self, *args, **kwargs):
        self.parent.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.parent.pack(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        self.press()

    def press(self, *args, **kwargs):
        self.config(bg=self.activebackground)
        self.variable.set(self.value)
        self.update()
        self.command()

    def set(self, number):
        if number == 0:
            self.config(text=" ")
        else:
            self.config(text=number)

        for item in self.grid_slaves():
            item.destroy()

        self.numbers = []

    def possible(self, numbers, *args, **kwargs):
        if "font" in kwargs.keys():
            fontStyle = kwargs["font"]
        else:
            fontStyle = "Courier 6"
            
        for i in range(3):
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

        self.numbers = []
        for number in range(1, 10):
            if number in numbers:
                self.numbers.append(tk.Label(self.master, text=number,
                                             borderwidth=0, padx=0, pady=0,
                                             font=fontStyle,
                                             fg=self.cget("fg")))
            else:
                self.numbers.append(tk.Label(self.master, text=" ",
                                             borderwidth=0, padx=0, pady=0,
                                             font=fontStyle,
                                             fg=self.cget("fg")))
                
            self.numbers[-1].grid(in_=self, row=(number-1)//3,
                                  column=(number-1)%3, sticky="nsew")

            self.numbers[-1].bind("<Button-1>", self.press)

    def update(self, *args, **kwargs):
        if self.variable.get() == self.value:
            self.config(bg=self.activebackground)
            for item in self.grid_slaves():
                item.config(bg=self.activebackground)
        else:
            self.config(bg=self.background)
            for item in self.grid_slaves():
                item.config(bg=self.background)

class MenuBar(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        tk.Menu.__init__(self, master=parent)
        self.master.configure(menu=self)
                
        self.fileMenu = tk.Menu(self, tearoff=False)
        self.fileMenu.add_command(label="Blank Sudoku", accelerator="Ctrl+B",
                                  command=self.master.newFile)
        self.fileMenu.add_command(label="Open...", accelerator="Ctrl+O",
                                  command=self.master.openFile)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Save", accelerator="Ctrl+S",
                                  command=self.master.saveFile)
        self.fileMenu.add_command(label="Save As...",
                                  accelerator="Ctrl+Shift+S",
                                  command=self.master.saveAsFile)
        self.fileMenu.add_command(label="Create Sudoku", accelerator="Ctrl+Z",
                                  command=self.master.createSudoku)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", accelerator="Alt+F4",
                                  command=self.master.closeWindow)
        self.add_cascade(label="File", menu=self.fileMenu)

        self.editMenu = tk.Menu(self, tearoff=False,
                                postcommand=self.master.timerStatus)
        self.editMenu.add_command(label=str(self.master.timerLabel),
                                  accelerator="Space",
                                  command=self.master.toggle)
        self.editMenu.add_command(label="Reset", accelerator="Ctrl+R",
                                  command=self.master.reset)
        self.editMenu.add_command(label="Check", accelerator="Ctrl+Enter",
                                  command=self.master.check)
        self.editMenu.add_command(label="Solve",accelerator="F5",
                                  command=self.master.solve)
        self.add_cascade(label="Edit", menu=self.editMenu)

        self.add_command(label="Format", command=self.format)

        self.optionsMenu = tk.Menu(self, tearoff=False)
        self.optionsMenu.add_checkbutton(label="Position",
                                         variable=self.master.positionVar,
                                         command=self.master.updateStatus)
        self.optionsMenu.add_checkbutton(label="Timer",
                                         variable=self.master.timerVar,
                                         command=self.master.updateStatus)
        self.optionsMenu.add_checkbutton(label="Error Highlighting",
                                         variable=self.master.errorVar,
                                         command=self.master.updateErrors)
        self.add_cascade(label="Options", menu=self.optionsMenu)
        
        self.master.bind("<Control-b>", self.master.newFile)
        self.master.bind("<Control-o>", self.master.openFile)
        self.master.bind("<Control-s>", self.master.saveFile)
        self.master.bind("<Control-Shift-S>", self.master.saveAsFile)
        self.master.bind("<Control-z>", self.master.createSudoku)          
        self.master.bind("<Alt-F4>", self.master.closeWindow)
        self.master.bind("<Control-w>", self.master.closeWindow)
        self.master.bind("<Control-r>", self.master.reset)
        self.master.bind("<Control-Return>", self.master.check)
        self.master.bind("<Control-KP_Enter>", self.master.check)
        self.master.bind("<space>", self.master.toggle)
        self.master.bind("<F5>", self.master.solve)

    def format(self, *args, **kwargs):
        def closeWindow(*args, **kwargs):
            self.master.style = formatWindow.getStyle()
            self.master.resize()
            
        formatWindow = FormatWindow(self.master, padx=7, pady=5,
                                    defaults=self.master.style,
                                    command=closeWindow)

class StatusBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        if "command" in kwargs.keys():
            self.command = kwargs.pop("command")
        else:
            self.command = None

        if "size" in kwargs.keys():
            size = kwargs.pop("size")
        else:
            size = 12

        self.font = font.Font(size=size)
            
        tk.Frame.__init__(self, *args, master=parent, **kwargs)

        if self.master.timerVar.get():
            self.timer = Timer(self, command=self.command, font=self.font)
            self.timer.pack(side="right")
        else:
            try:
                self.timer.pack_forget()
            except:
                pass

        pos = self.master.gridFrame.position.get()
        row = int(pos[0]) + 1
        column = int(pos[1]) + 1

        if self.master.positionVar.get():
            self.selected = tk.Label(self, font=self.font,
                                     text="Row: {} Column: {}"
                                     .format(row, column))
            self.selected.pack(side="left")
        else:
            try:
                self.selected.pack_forget()
            except:
                pass

    def reset(self, *args, **kwargs):
        self.timer.reset()

    def play(self, *args, **kwargs):
        self.timer.play()

    def pause(self, *args, **kwargs):
        return self.timer.pause()

    def toggle(self, *args, **kwargs):
        self.timer.toggle()

    def setTime(self, minutes, seconds, *args, **kwargs):
        self.timer.setTime(minutes, seconds)

    def getTime(self, *args, **kwargs):
        return self.timer.getTime()

    def updatePos(self, *args, **kwargs):
        pos = self.master.gridFrame.position.get()
        row = int(pos[0]) + 1
        column = int(pos[1]) + 1
        
        self.selected.config(text="Row: {} Column: {}".format(row, column))

    def updateStatus(self, *args, **kwargs):
        if self.master.timerVar.get():
            self.timer.pack(side="right")
        else:
            try:
                self.timer.pack_forget()
            except:
                pass

        if self.master.positionVar.get():
            self.selected.pack(side="left")
        else:
            try:
                self.selected.pack_forget()
            except:
                pass

    def getStatus(self, *args, **kwargs):
        return self.timer.status

    def redraw(self, *args, **kwargs):
        self.timer.update()

    def setSize(self, size):
        self.font = font.Font(size=size)
        self.timer.config(font=self.font)
        self.selected.config(font=self.font)

class Timer(tk.Label):
    def __init__(self, parent, *args, **kwargs):
        if "command" in kwargs.keys():
            self.command = kwargs.pop("command")
        else:
            self.command = None
            
        tk.Label.__init__(self, *args, master=parent, **kwargs)

        self.status = "play"

        self.bind("<Button-1>", self.toggle)

        self.reset()
        self.after(1000, self.increment)

    def increment(self, *args, **kwargs):
        if self.status == "play":
            self.count += 1
            
        self.update()
        self.after(1000, self.increment)

    def reset(self, *args, **kwargs):
        self.count = 0

        self.config(text="00:00")

    def update(self, *args, **kwargs):
        minutes, seconds = self.getTime()
        
        self.config(text="{}:{}".format(str(minutes).rjust(2, "0"),
                                        str(seconds).rjust(2, "0")))

    def play(self, *args, **kwargs):
        self.status = "play"

    def pause(self, *args, **kwargs):
        self.status = "pause"
        return self.getTime()

    def toggle(self, *args, **kwargs):
        if self.status == "play":
            self.pause()
        else:
            self.play()

        if self.command != None:
            self.command()

    def setTime(self, minutes, seconds, *args, **kwargs):
        total = (60 * minutes) + seconds
        self.count = total

    def getTime(self, *args, **kwargs):
        elapsed = self.count
        minutes = elapsed // 60
        seconds = elapsed % 60
        return (minutes, seconds)

class FormatWindow(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        if "defaults" in kwargs.keys():
            self.style = kwargs.pop("defaults")
        else:
            self.style = {"size": 19, "width": 1, "colour": "#000000",
                          "error": "#FF0000", "line": "#000000"}

        if "width" in self.style.keys():
            width = self.style["width"]
        else:
            width = 1

        if "colour" in self.style.keys():
            self.colour = self.style["colour"]
        else:
            self.colour = "#000000"

        if "error" in self.style.keys():
            self.error = self.style["error"]
        else:
            self.error = "#FF0000"

        if "line" in self.style.keys():
            self.line = self.style["line"]
        else:
            self.line = "#000000"

        if "start" in self.style.keys():
            self.start = self.style["start"]
        else:
            self.start = "#000000"

        if "command" in kwargs.keys():
            self.command = kwargs.pop("command")
        else:
            self.command = None
            
        tk.Toplevel.__init__(self, *args, master=parent, **kwargs)
        self.title("Format")

        self.sizes = {"Extra Small": 16, "Small": 19, "Medium": 22, "Large": 25,
                      "Extra Large": 28, "Huge": 31, "Extra Huge": 34}

        self.sizeLabel = tk.Label(self, text="Size: ")
        self.sizeLabel.grid(row=0, column=0, sticky="e", pady=2)
        self.sizeCombo = ttk.Combobox(self, values=list(self.sizes.keys()),
                                      state="readonly")
        self.sizeCombo.grid(row=0, column=1, sticky="ew", pady=2)
        self.sizeCombo.set(list(self.sizes.keys())[list(self.sizes.values())
                                                   .index(self.style["size"])])

        self.widthLabel = tk.Label(self, text="Line Width: ")
        self.widthLabel.grid(row=1, column=0, sticky="e", pady=2)
        self.widthCombo = ttk.Combobox(self, values=list(range(0, 6)),
                                       state="readonly")
        self.widthCombo.grid(row=1, column=1, sticky="ew", pady=2)
        self.widthCombo.set(width)

        self.startLabel = tk.Label(self, text="Start Colour: ")
        self.startLabel.grid(row=2, column=0, sticky="e", pady=2)
        self.startButton = tk.Button(self, command=self.getStartColour,
                                     bg=self.start)
        self.startButton.grid(row=2, column=1, sticky="ew", pady=2)

        self.colourLabel = tk.Label(self, text="Number Colour: ")
        self.colourLabel.grid(row=3, column=0, sticky="e", pady=2)
        self.colourButton = tk.Button(self, command=self.getNumberColour,
                                      bg=self.colour)
        self.colourButton.grid(row=3, column=1, sticky="ew", pady=2)

        self.errorLabel = tk.Label(self, text="Error Colour: ")
        self.errorLabel.grid(row=4, column=0, sticky="e", pady=2)
        self.errorButton = tk.Button(self, command=self.getErrorColour,
                                     bg=self.error)
        self.errorButton.grid(row=4, column=1, sticky="ew", pady=2)

        self.lineLabel = tk.Label(self, text="Line Colour: ")
        self.lineLabel.grid(row=5, column=0, sticky="e", pady=2)
        self.lineButton = tk.Button(self, command=self.getLineColour,
                                     bg=self.line)
        self.lineButton.grid(row=5, column=1, sticky="ew", pady=2)

        self.buttonFrame = tk.Frame(self)
        self.buttonFrame.grid(row=6, column=0, columnspan=2)
        
        self.okButton = ttk.Button(self.buttonFrame, text="Ok",
                                   command=self.closeWindow)
        self.okButton.grid(row=0, column=0, padx=2, pady=2)
        self.cancelButton = ttk.Button(self.buttonFrame, text="Cancel",
                                       command=self.destroy)
        self.cancelButton.grid(row=0, column=1, padx=2, pady=2)

        self.focus_force()

    def getNumberColour(self, *args, **kwargs):
        old = self.colour
        
        self.colour = askcolor(parent=self, color=self.colour,
                               title="Number Colour")[1]

        if self.colour != None:
            self.colourButton.config(bg=self.colour)
        else:
            self.colour = old

        self.focus_force()

    def getErrorColour(self, *args, **kwargs):
        old = self.error
        
        self.error = askcolor(parent=self, color=self.error,
                              title="Error Colour")[1]

        if self.error != None:
            self.errorButton.config(bg=self.error)
        else:
            self.error = old

        self.focus_force()

    def getLineColour(self, *args, **kwargs):
        old = self.line
        
        self.line = askcolor(parent=self, color=self.line,
                             title="Line Colour")[1]

        if self.line != None:
            self.lineButton.config(bg=self.line)
        else:
            self.line = old

        self.focus_force()

    def getStartColour(self, *args, **kwargs):
        old = self.start
        
        self.start = askcolor(parent=self, color=self.start,
                              title="Start Colour")[1]

        if self.start != None:
            self.startButton.config(bg=self.start)
        else:
            self.start = old

        self.focus_force()
        
    def setStyle(self, *args, **kwargs):
        self.style = {"size": self.sizes[self.sizeCombo.get()],
                      "width": self.widthCombo.get(), "colour": self.colour,
                      "error": self.error, "line": self.line,
                      "start": self.start}

    def getStyle(self, *args, **kwargs):
        return self.style

    def closeWindow(self, *args, **kwargs):
        self.setStyle()
        self.destroy()
        self.master.saveData()

        if self.command != None:
            self.command()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = None
        
    root = Sudoku(directory=appData+"\\Sudoku\\",
                  fileName=fileName)
    root.mainloop()
