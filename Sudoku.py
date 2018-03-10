import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
from tkinter import font

import csv
import os
import sys
import shutil
import time
import pickle
from copy import deepcopy

appData = os.getenv("LOCALAPPDATA")

if not "Sudoku" in os.listdir(appData):
    os.makedirs(appData+"\\Sudoku\\")

if not "Puzzles" in os.listdir(appData+"\\Sudoku\\"):
    shutil.copytree(os.getcwd()+"\\Puzzles", appData+"\\Sudoku\\Puzzles")
    
if not "programData.pkl" in os.listdir(appData+"\\Sudoku\\"):
    data = {"filename": appData+"\\Sudoku\\Puzzles\\Easy\\Easy 1.puz",
            "timer": True, "position": True}
    
    pickle.dump(data, open(appData+"\\Sudoku\\programData.pkl", "wb"))

class Sudoku(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self)
        self.title("Sudoku")
        self.iconbitmap(default="Files\\logo.ico")

        self.protocol("WM_DELETE_WINDOW", self.closeWindow)

        self.resizable(False, False)

        self.menuBar = MenuBar(self)

        self.gridFrame = GridFrame(self)
        self.gridFrame.pack(fill="both", expand=True)

        if "directory" in kwargs.keys():
            self.directory = kwargs["directory"]
        else:
            self.directory = os.getcwd()

        self.statusBar = StatusBar(self)
        self.statusBar.pack(side="bottom", fill="x", expand=True)

        fileName = None
        if "fileName" in kwargs.keys():
            fileName = kwargs["fileName"]
        if fileName == None:
            fileName = self.loadData()

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
        self.statusBar.pause()
        
        self.gridFrame.saveAsFile(*args, minutes=minutes, seconds=seconds,
                                  fileName=self.fileName, **kwargs)

        self.statusBar.play()

    def saveAsFile(self, *args, **kwargs):
        minutes, seconds = self.statusBar.getTime()
        self.statusBar.pause()
        
        self.gridFrame.saveAsFile(*args, minutes=minutes, seconds=seconds,
                                  **kwargs)

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

            self.gridFrame.update()
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
"""Congratulations! You have completed the sudoku.
Do you want to save your solution?""".format(minutes, seconds))

            if save != None:
                if save:
                    self.saveAsFile(fileName=self.fileName)
                self.statusBar.pause()
        else:
            messagebox.showinfo("Not quite.",
                "Not quite. There is an error in your solution.")

    def helpWindow(self, *args, **kwargs):
        pass
        #window = HelpWindow()

    def setTime(self, minutes, seconds, *args, **kwargs):
        self.statusBar.setTime(minutes, seconds)

    def getTime(self, *args, **kwargs):
        return self.statusBar.getTime()

    def updatePos(self, *args, **kwargs):
        self.statusBar.updatePos()

    def updateStatus(self, *args, **kwargs):
        self.statusBar.updateStatus()

        if self.timerVar.get() or self.positionVar.get():
            self.statusBar.pack(side="bottom", fill="x", expand=True)
        else:
            self.statusBar.pack_forget()

    def saveData(self, *args, **kwargs):
        if "fileName" in kwargs.keys():
            fileName = kwargs["fileName"]
        else:
            fileName = self.fileName
            
        data = {"filename": fileName, "timer": self.timerVar.get(),
                "position": self.positionVar.get()}
        
        pickle.dump(data, open(self.directory+"programData.pkl", "wb"))

    def loadData(self, *args, **kwargs):
        data = pickle.load(open(self.directory+"programData.pkl", "rb"))

        fileName = data["filename"]
        self.timerVar.set(data["timer"])
        self.positionVar.set(data["position"])

        self.updateStatus()

        return fileName

    def toggle(self, *args, **kwargs):
        self.statusBar.toggle()

class GridFrame(tk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent

        self.frame = tk.Frame(self, borderwidth=2, relief="solid",
                              highlightbackground="BLACK")
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.normalFont = font.Font(family="Courier", size=18, weight="normal")
        self.boldFont = font.Font(family="Courier",
                                  size=self.normalFont["size"], weight="bold")
        self.smallFont = font.Font(family="Courier",
                                   size=int(self.normalFont["size"]/3))

        self.lineColour = "BLACK"
        self.activeColour = "WHITE"
        self.lineRelief = "solid"
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
    
        for n in range(9):
            self.frame.rowconfigure(n+n//3, weight=1)
            self.frame.columnconfigure(n+n//3, weight=1)

        self.line1 = tk.Frame(self.frame, borderwidth=1, relief=self.lineRelief,
                              background=self.lineColour, width=1)
        self.line1.grid(row=0, column=3, rowspan=11, sticky="nsew")
        self.line2 = tk.Frame(self.frame, borderwidth=1, relief=self.lineRelief,
                              background=self.lineColour, width=1)
        self.line2.grid(row=0, column=7, rowspan=11, sticky="nsew")
        self.line3 = tk.Frame(self.frame, borderwidth=1, relief=self.lineRelief,
                              background=self.lineColour, height=1)
        self.line3.grid(row=3, column=0, columnspan=11, sticky="nsew")
        self.line4 = tk.Frame(self.frame, borderwidth=1, relief=self.lineRelief,
                              background=self.lineColour, height=1)
        self.line4.grid(row=7, column=0, columnspan=11, sticky="nsew")
        
        self.position = tk.StringVar()
        self.position.set("00")

        self.newFile()

        self.parent.bind("<Key>", self.keyPressed)
        self.parent.bind("<Button-1>", self.callback)
        self.parent.bind("<Up>", self.upKey)
        self.parent.bind("<Down>", self.downKey)
        self.parent.bind("<Left>", self.leftKey)
        self.parent.bind("<Right>", self.rightKey)
        self.parent.bind("<BackSpace>", self.backSpaceKey)

    def update(self, *args, **kwargs):
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
                                          font=fontStyle, borderwidth=1,
                                          relief=self.lineRelief,
                                          highlightbackground=self.lineColour,
                                          activebackground=self.activeColour,
                                          indicatoron=0, width=2,
                                          padx=0, pady=0))
                self.cells[r][c].grid(row=r+r//3, column=c+c//3, sticky="nsew")
                
                if self.grid[r][c] != 0:
                    self.cells[r][c].set(self.grid[r][c])
                elif self.possible[r][c] != []:
                    self.cells[r][c].possible(self.possible[r][c],
                                              font=self.smallFont)
                else:
                    self.cells[r][c].set(0)

    def updateCells(self, *args, **kwargs):
        for row in self.cells:
            for cell in row:
                cell.update()

        self.parent.updatePos()

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

    def callback(self, event):
        self.focus_set()

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

        self.parent.fileName = None
        self.parent.title("Untitled - Sudoku")

        self.initialStart = deepcopy(self.start)
        self.initialGrid = deepcopy(self.grid)
        self.initialPossible = deepcopy(self.possible)

        self.update()

    def openFile(self, *args, **kwargs):
        oldFileName = self.parent.fileName
        oldStart = deepcopy(self.start)
        oldGrid = deepcopy(self.grid)
        oldPossible = deepcopy(self.possible)

        minutes = 0
        seconds = 0

        fileName = None
        if "fileName" in kwargs.keys():
            fileName = kwargs["fileName"]
        if fileName == None:
            fileName = askopenfilename(parent=self.parent,
                                       initialdir=self.parent.directory
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

            self.parent.fileName = fileName
            if "\\" in fileName:
                self.parent.title("{} - Sudoku".format(fileName.split("\\")[-1]
                                                       .replace(".puz", "")))
            else:
                self.parent.title("{} - Sudoku".format(fileName.split("/")[-1]
                                                       .replace(".puz", "")))

            self.initialStart = deepcopy(self.start)
            self.initialGrid = deepcopy(self.grid)
            self.initialPossible = deepcopy(self.possible)

            self.parent.saveData(fileName=fileName)
                
        except FileNotFoundError:
            self.parent.fileName = oldFileName
            if "\\" in oldFileName:
                self.parent.title("{} - Sudoku"
                                  .format(oldFileName.split("\\")[-1]
                                          .replace(".puz", "")))
            else:
                self.parent.title("{} - Sudoku"
                                  .format(oldFileName.split("/")[-1]
                                          .replace(".puz", "")))
                
            self.start = deepcopy(oldStart)
            self.grid = deepcopy(oldGrid)
            self.possible = deepcopy(oldPossible)
        except:
            self.start = deepcopy(oldStart)
            self.grid = deepcopy(oldGrid)
            self.possible = deepcopy(oldPossible)

        self.update()
        return (minutes, seconds)

    def saveAsFile(self, *args, **kwargs):
        fileName = None
        if "fileName" in kwargs.keys():
            fileName = kwargs["fileName"]
        if fileName == None:
            fileName = asksaveasfilename(parent=self.parent,
                                         initialdir=self.parent.directory
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

                m, s = self.parent.getTime()
                if minutes != 0 or seconds != 0:
                    csvwriter.writerow([minutes, seconds])
                else:
                    csvwriter.writerow([m, s])

            self.parent.fileName = fileName
            if "\\" in fileName:
                self.parent.title("{} - Sudoku".format(fileName.split("\\")[-1]
                                                       .replace(".puz", "")))
            else:
                self.parent.title("{} - Sudoku".format(fileName.split("/")[-1]
                                                       .replace(".puz", "")))

            self.initialStart = deepcopy(self.start)
            self.initialGrid = deepcopy(self.grid)
            self.initialPossible = deepcopy(self.possible)

            self.parent.saveData()
                
        except PermissionError:
            messagebox.showerror("Permission Error",
    "Sudoku is unable to save to this file as it is open in another program.")
        except FileNotFoundError:
            pass

    def createSudoku(self, *args, **kwargs):
        fileName = asksaveasfilename(parent=self.parent,
                                     initialdir=self.parent.directory
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

    def modified(self, *args, **kwargs):
        if self.initialStart != self.start:
            return True
        if self.initialGrid != self.grid:
            return True
        if self.initialPossible != self.possible:
            return True
        return False

class Cell(tk.Radiobutton):
    def __init__(self, parent, *args, **kwargs):
        tk.Radiobutton.__init__(self, parent, *args, **kwargs)
        
        self.parent = parent

        if "variable" in kwargs.keys():
            self.variable = kwargs["variable"]
        if "value" in kwargs.keys():
            self.value = kwargs["value"]

        self.background = self.cget("background")
        self.activebackground = self.cget("activebackground")
        
        self.numbers = []

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
                self.numbers.append(tk.Label(self.parent, text=number,
                                             borderwidth=0, padx=0, pady=0,
                                             font=fontStyle))
            else:
                self.numbers.append(tk.Label(self.parent, text=" ",
                                             borderwidth=0, padx=0, pady=0,
                                             font=fontStyle))
                
            self.numbers[-1].grid(in_=self, row=(number-1)//3,
                                  column=(number-1)%3, sticky="nsew")

            self.numbers[-1].bind("<Button-1>", self.callback)

    def callback(self, event):
        self.invoke()

    def update(self, *args, **kwargs):
        if self.variable.get() == self.value:
            for item in self.grid_slaves():
                item.configure(background=self.activebackground)
        else:
            for item in self.grid_slaves():
                item.configure(background=self.cget("background"))

class MenuBar(tk.Menu):
    def __init__(self, parent, *args, **kwargs):
        tk.Menu.__init__(self, parent)
        parent.config(menu=self)

        self.parent = parent

        self.fileMenu = tk.Menu(self, tearoff=False)
        self.fileMenu.add_command(label="New Sudoku", accelerator="Ctrl+N",
                                  command=self.parent.newFile)
        self.fileMenu.add_command(label="Open...", accelerator="Ctrl+O",
                                  command=self.parent.openFile)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Save", accelerator="Ctrl+S",
                                  command=self.parent.saveFile)
        self.fileMenu.add_command(label="Save As...",
                                  accelerator="Ctrl+Shift+S",
                                  command=self.parent.saveAsFile)
        self.fileMenu.add_command(label="Create Sudoku", accelerator="Ctrl+Z",
                                  command=self.parent.createSudoku)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", accelerator="Alt+F4",
                                  command=self.parent.closeWindow)
        self.add_cascade(label="File", menu=self.fileMenu)

        self.parent.timerVar = tk.BooleanVar()
        self.parent.timerVar.set(True)
        
        self.parent.positionVar = tk.BooleanVar()
        self.parent.positionVar.set(True)

        self.optionsMenu = tk.Menu(self, tearoff=False)
        self.optionsMenu.add_checkbutton(label="Timer",
                                         variable=self.parent.timerVar,
                                         command=self.parent.updateStatus)
        self.optionsMenu.add_checkbutton(label="Position",
                                         variable=self.parent.positionVar,
                                         command=self.parent.updateStatus)
        self.optionsMenu.add_separator()
        self.optionsMenu.add_command(label="Reset", accelerator="Ctrl+R",
                                     command=self.parent.reset)
        self.optionsMenu.add_command(label="Check", accelerator="Ctrl+Enter",
                                     command=self.parent.check)
        self.optionsMenu.add_command(label="Play / Pause", accelerator="Space",
                                     command=self.parent.toggle)
        self.add_cascade(label="Options", menu=self.optionsMenu)
        
        #self.add_command(label="Help", command=self.parent.helpWindow)

        self.parent.bind("<Control-n>", self.parent.newFile)
        self.parent.bind("<Control-o>", self.parent.openFile)
        self.parent.bind("<Control-s>", self.parent.saveFile)
        self.parent.bind("<Control-Shift-S>", self.parent.saveAsFile)
        self.parent.bind("<Control-z>", self.parent.createSudoku)          
        self.parent.bind("<Alt-F4>", self.parent.closeWindow)
        self.parent.bind("<Control-w>", self.parent.closeWindow)
        self.parent.bind("<Control-r>", self.parent.reset)
        self.parent.bind("<Control-Return>", self.parent.check)
        self.parent.bind("<Control-KP_Enter>", self.parent.check)
        self.parent.bind("<space>", self.parent.toggle)

class StatusBar(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, *args, master=parent, **kwargs)

        if self.master.timerVar.get():
            self.timer = Timer(self)
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
            self.selected = tk.Label(self,
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

    def redraw(self, *args, **kwargs):
        self.timer.update()

class Timer(tk.Label):
    def __init__(self, parent, *args, **kwargs):
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

    def pause(self, *args, **kwargs):
        self.status = "pause"
        return self.getTime()

    def play(self, *args, **kwargs):
        self.status = "play"

    def toggle(self, *args, **kwargs):
        if self.status == "play":
            self.pause()
        else:
            self.play()

    def setTime(self, minutes, seconds, *args, **kwargs):
        total = (60 * minutes) + seconds
        self.count = total

    def getTime(self, *args, **kwargs):
        elapsed = self.count
        minutes = elapsed // 60
        seconds = elapsed % 60
        return (minutes, seconds)

class HelpWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Help")

        self.text = tk.Text(self, text=message)
        self.text.pack(fill="both", expand=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = None
        
    root = Sudoku(directory=appData+"\\Sudoku",
                  fileName=fileName)
    root.mainloop()
