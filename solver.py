from copy import deepcopy

class Solver(object):
    def __init__(self, start):
        self.start = start
        self.grid = deepcopy(start)
        self.possible = []

    def solve(self, *args, **kwargs):
        self.findPossible()
        
        run = True
        while run:
            old = deepcopy(self.grid)
            
            self.findNumbers()

            if self.grid == old:
                self.findNumbers1()

                if self.grid == old:
                    run = False
            else:
                run = not self.check()

        return self.getGrid()

    def resetPossible(self, *args, **kwargs):
        for r in range(9):
            self.possible.append([])
            for c in range(9):
                self.possible[r].append([])

    def findPossible(self, *args, **kwargs):
        self.resetPossible()
        for i in range(9):
            box = self.getBox(i)
            for n in range(9):
                r = 3 * (i // 3) + n // 3
                c = 3 * (i % 3) + n % 3
                row = self.grid[r]
                column = self.getCol(c)
                for number in range(1, 10):
                    if not (number in box or number in row
                            or number in column) and self.start[r][c] == 0:
                        self.possible[r][c].append(number)

    def findNumbers(self, *args, **kwargs):
        for r in range(9):
            for c in range(9):
                if len(self.possible[r][c]) == 1:
                    self.setNumber(r, c, self.possible[r][c][0])

    def findNumbers1(self, *args, **kwargs):
        for i in range(9):
            for c in range(9):
                for number in self.possible[i][c]:
                    unique = True
                    for x in range(9):
                        if x != c:
                            if number in self.possible[i][x]:
                                unique = False
                                break
                            
                    if unique == True:
                        self.setNumber(i, c, number)

            column = []
            for n in range(9):
                column.append(self.possible[n][i])

            for r in range(9):
                for number in column[r]:
                    unique = True
                    for x in range(9):
                        if x != r:
                            if number in column[x]:
                                unique = False
                                break
                            
                    if unique == True:
                        self.setNumber(r, i, number)

            box = []
            for n in range(9):
                r = 3 * (i // 3) + n // 3
                c = 3 * (i % 3) + n % 3
                box.append(self.possible[r][c])
                
            for n in range(9):
                for number in box[n]:
                    unique = True
                    for x in range(9):
                        if x != n:
                            if number in box[x]:
                                unique = False
                                break
                            
                    if unique == True:
                        r = 3 * (i // 3) + n // 3
                        c = 3 * (i % 3) + n % 3
                        self.setNumber(r, c, number)

    def getGrid(self, *args, **kwargs):
        return (self.start, self.grid, self.possible)

    def setNumber(self, r, c, number):
        if self.start[r][c] == 0:
            self.grid[r][c] = number
            self.possible[r][c] = []
            for i in range(9):
                self.possible[r][i] = [x for x in self.possible[r][i]
                                       if x != number]
                self.possible[i][c] = [x for x in self.possible[i][c]
                                       if x != number]
                n = 3 * (r // 3) + c // 3
                a = 3 * (n // 3) + i // 3
                b = 3 * (n % 3) + i % 3
                self.possible[a][b] = [x for x in self.possible[a][b]
                                       if x != number]

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
