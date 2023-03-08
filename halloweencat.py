from PIL import Image, ImageDraw
import mouseinfo
import pyautogui
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Listener
import keyboard
# from pynput.keyboard import Key, Controller
import time
import random

#DO THIS: make sure zoom is 100%
#Make sure halloween cat is in the first monitor/main screen and the cmd line doesn't block the screenshot
#HOLD DOWN Q TO SHUT IT OFF


PATH = r'C:\Users\677708\Downloads\Halloween_Cat' # r'D:\PyCharm Projects\Halloween_Cat' # The path to where the python file is. RECOMMENDATION: It is recommended that you put it in its own folder so that saved screenshots are easy to find

'''
The fun part of this project was balancing Time vs. Efficency. If I search every pixel, it takes forever, but it will always get symbols, but if I search infrequently it can miss some, espeically the small lines
Some options:
mindisplacement: The minimum displacement aka how many pixels it skips every search - 
    min will be used if two symbols were seen last turn, meaning there's lots of symbols so we might want to search more accuratly, so we don't skip one and waste a turn
maxdisplacement: The maximum displacement aka how many pixels it skips every search - 
    max will be used if it didn't see many symbols. It's more important to just search more often than accuratly
Setting these equal will make it just work at that rate all the time if you don't agree
colortolerance: The tolerance of the color comparisions, so that it might more easily pick up edges
sleep: How much sleep it takes when drawing symbols
    lower sleep will of course speed it up (slightly) but sometimes the game will inaccuratly read the mouse inputs and it won't draw the symbol you want, which can be bad
symbols
    The number of symbols till we go to take a new screenshot: 1 means each symbol drawn we'll take a new screenshot, 4 means we'll draw 4 (different) symbols before deciding to take a new screenshot
    DON'T MAKE THIS TOO BIG SINCE YOU CAN'T DRAW DUPLICATES
    This is because it will read the same symbol multiple times, so to prevent that, we just don't draw the same symbol again
    The bigger the number, the longer each loop will be, but it might draw more symbols. Actually, lets print that! Lightning will make it a little off though
You mostly want to mess with displacement, it will have the most impact
The numbers I have I found are best for looking cool and like it's working, as well as highscore, but it does die sometimes in return
Here's some patterns
Lower Symbols Is going to get a higher score from streaks, but it reads the same symbol sometimes so you have to increase SCREENSHOTSLEEP more to account for that
Higher Symbols will be more spammy. It will look cool sometimes, and look like an idiot others. Like on long strings of the same symbol where it does symbols farther down the list way too soon
The biggest issue with low symbols is quick time, both the section 3 boss and the fast ghosts in section 4, but it's just a life here or there
This is especially true for the thin lines that can sometimes be skipped by the program. Which is sadly most of section 4's fast ghosts, although I'm realizing there might be more of the other fast ones, they just die
The biggest issue with high symbols is long strings of the same symbol
There's more but I'll write them later (maybe)
Yeah I'm not going to lol, have fun messing with it yourself, and I've messed with so much I forgotten so much and there's so many things already
'''
SCREENSHOTSLEEP = .025 #At least .0008

myScreenshot = pyautogui.screenshot()
search = pyautogui.locateOnScreen(PATH+r'\screenshots\search.png',confidence = .5)
print(search)

X1 = search.left-50
Y1 = search.top-50
SWIDTH = search.width+100
SHEIGHT = search.height+100

def newScreenshot(game): #This should be part of the game class in the future, so I can mess with its sleep more easily
  mouse.position = (0, 200)
  time.sleep(SCREENSHOTSLEEP) #Get the mouse out of the way ALSO: Added some extra sleep here to let the screen clear a bit
  myScreenshot = pyautogui.screenshot(region=(X1, Y1, SWIDTH, SHEIGHT))
  #if game.finalBoss:
      #boxImage = ImageDraw.Draw(myScreenshot) #Draw a rectangle where it doesn't read input
      #boxImage.rectangle([(470,180),(870,445)], fill ="black", outline ="black")
      #boxImage.rectangle([(280,425),(420,530)], fill ="black", outline ="black")
  #myScreenshot.save(PATH + r'\screenshots\curr.png') #THIS TAKES A REALLY LONG TIME! Like, it's really really slow. 
  return myScreenshot



class Game:
  def __init__(self):  # Defines all variables
    #These shouldn't change
    self.red = (252,3,4)
    self.blue = (12,101,214)
    self.yellow = (255,245,45)
    self.green = (29,255,32)
    self.lightning = (253,190,6)
    self.white = (255,255,255)
    #self.finalcolor = (236, 216, 192)
    self.bossChecks = [(800, 675),(1200,675)]
    self.finalBoss = False
    self.prevTime = time.perf_counter()
    self.screenshot = newScreenshot(self)
    self.count = 0 #How many symbols drawn each loop
    self.shift = 0 #The shift over so it searches different rows and columns
    
    #These can change
    self.sleep = 0.001
    self.colortolerance = 10
    self.mindisplacement = 3
    self.maxdisplacement = 4
    self.symbols = 3 #The number of symbols till we go to take a new screenshot: 1 means each symbol drawn we'll take a new screenshot. #DON'T MAKE THIS TOO BIG SINCE YOU CAN'T DRAW DUPLICATES
    #1: Highest score
    #3: Coolest (imo)
    
    #This shouldn't change but is reliant on the previous values
    self.displacement = self.mindisplacement #How far apart it searches 
   
  def isAboutColor(self,color,ocolor): #Tuple: color
    tolerance = self.colortolerance
    return (color[0] < ocolor[0]+tolerance and color[0] > ocolor[0]-tolerance) and (color[1] < ocolor[1]+tolerance and color[1] > ocolor[1]-tolerance) and (color[2] < ocolor[2]+tolerance and color[2] > ocolor[2]-tolerance)
  
  def click(self,x,y):
    mouse.position = (x+X1,y+Y1) #Click on the photo with offsets to where the photo is taken
    mouse.click(Button.left)
    
  def printinfo(self):
    print(f"Shift: {self.shift}\nDisplacement: {self.displacement}\nFinal Boss: {self.finalBoss}\nTime (ms): {(time.perf_counter() - self.prevTime)*1000:.0f}\nSymbols Drawn: {self.count}")
    self.prevTime = time.perf_counter()
    
  def searchBoard(self): #Draws two symbols, but never duplicates sadly
    self.shift = (self.shift + 1)%self.displacement #Add one to shift, but not more than the current displacement
    red = False
    blue = False
    yellow = False
    green = False
    self.printinfo()
    self.count = 0
    for x in range(0+self.shift,SWIDTH,self.displacement): #Then Left to Right Otherwise it doesn't see the reds -V It reads the top left of the V before the -, so we go top to bottom before going left
        for y in range(0+self.shift,SHEIGHT,self.displacement):  #Top to Bottom
            #not self.finalBoss is a test if the drawing is much of an issue so I don't cover much space, and if so, I should lower the size of the original box Could also draw in the bottom right corner but I don't want to do that
            if (not self.finalBoss and 470 < x < 870 and 180 < y < 445) or (self.finalBoss and 250 < x < 450 and 455 < y < 560):
                continue
            color = self.screenshot.getpixel((x,y))
            if self.isAboutColor(color, self.red) and not red:
                self.drawHorizontal()
                self.count += 1
                red = True
            elif self.isAboutColor(color, self.blue) and not blue:
                self.drawVertical()
                self.count += 1
                blue = True
            elif self.isAboutColor(color, self.green) and not green:
                self.drawA()
                self.count += 1
                green = True
            elif self.isAboutColor(color, self.yellow) and not yellow:
                self.drawV()
                self.count += 1
                yellow = True
            elif self.isAboutColor(color, self.lightning):
                self.drawLightning()
                self.count += self.symbols #Once we do lightning, our screenshot is really wrong, so we'll skip to the end
            if self.count >= self.symbols: #If we've drawn more symbols than we're allowing, to allow for a screenshot reset
                self.displacement = self.mindisplacement
                return
            
    self.displacement = self.maxdisplacement
    
  def run(self):
    
    self.screenshot = newScreenshot(self)
    
    if not self.finalBoss:
        finalBoss = True
        for x in self.bossChecks:
            if self.screenshot.getpixel(x) != self.white:
                finalBoss = False
                break
        self.finalBoss = finalBoss
    #else:
    #    self.maxdisplacement = self.mindisplacement #Search More in the boss since things are smaller.  This slows it down too much I think it's better to go faster
    
    self.searchBoard()
  
  def centerofScreen(self):
    if self.finalBoss:
        return (X1+350,Y1+478)
    return (X1+SWIDTH//2,Y1+SHEIGHT//2)
    

  def drawHorizontal(self):
    center = self.centerofScreen()
    start = center[0]-150
    end = center[0]+150
    mouse.position = (start,center[1])
    mouse.press(Button.left)
    for i in range(start,end,50):
        time.sleep(self.sleep)
        mouse.position = (i,center[1])
    time.sleep(self.sleep)
    #time.sleep(0.25)
    mouse.release(Button.left)
    
  def drawVertical(self):
    center = self.centerofScreen()
    start = center[1]-150
    end = center[1]+100
    mouse.position = (center[0],start)
    mouse.press(Button.left)
    for i in range(start,end,50):
        time.sleep(self.sleep)
        mouse.position = (center[0],i)
    time.sleep(self.sleep)
    #time.sleep(0.25)
    mouse.release(Button.left)
   
  def drawA(self):
    center = self.centerofScreen()
    start = (center[0]-100,center[1])
    #middle = (center[0],center[1]+100)
    #end = (center[0]+100,center[1]-100)
    mouse.position = start
    mouse.press(Button.left) #A's and V's are inconsistent, I'm adding more sleep
    for i in range(0,100,50):
        time.sleep(self.sleep*2)
        mouse.move(50,-50)
    time.sleep(self.sleep*4)
    for i in range(0,100,50):
        time.sleep(self.sleep*2)
        mouse.move(50,50)
    time.sleep(self.sleep*6)
    mouse.release(Button.left)
    
  def drawV(self):
    center = self.centerofScreen()
    start = (center[0]-100,center[1]-100)
    #middle = (center[0],center[1]+100)
    #end = (center[0]+100,center[1]-100)
    mouse.position = start
    mouse.press(Button.left) #A's and V's are inconsistent, I'm adding more sleep
    for i in range(0,100,50):
        time.sleep(self.sleep*2)
        mouse.move(50,50)
    time.sleep(self.sleep*4)
    for i in range(0,100,50):
        time.sleep(self.sleep*2)
        mouse.move(50,-50)
    time.sleep(self.sleep*6)
    mouse.release(Button.left)
  
  def drawLightning(self):
    center = self.centerofScreen()
    start = (center[0]+25,center[1]-100)
    mouse.position = start
    mouse.press(Button.left)
    for i in range(0,100,50):
        time.sleep(0.001)
        mouse.move(-50,50)
    for i in range(0,100,50):
        time.sleep(0.001)
        mouse.move(50,0)
    for i in range(0,100,50):
        time.sleep(0.001)
        mouse.move(-50,50)
    time.sleep(0.001)
    mouse.release(Button.left)
    

  def playing(self):  # Sees if the game is being played or not
    return True
    global myScreenshot #This just isn't working for some reason so you can just shut it down yourself
    if self.finalBoss:
        #return self.isAboutColor(self.screenshot.getpixel((SWIDTH//2,SHEIGHT//2)),(236, 216, 192))
        return self.screenshot.getpixel((SWIDTH//2,SHEIGHT//2)) == (236, 216, 192)
    return True
        
mouse = Controller()
myGame = Game()

myScreenshot = pyautogui.screenshot(region=(X1, Y1, SWIDTH, SHEIGHT))  # Use PIL's instead?
myScreenshot.save(PATH + r'\screenshots\game.png')


# keyboard = Controller()

# listen = Listener(
#     on_press = on_press
# )
# listen.start()

# time.sleep(SLEEP)

myGame.click(SWIDTH//2, SHEIGHT//2)
time.sleep(1)
myGame.click(SWIDTH-100, SHEIGHT-10)
#myGame.clickTile(0,0)


#time.sleep(3) Auto plays the beginning, but running our code works to and is faster
#myGame.drawHorizontal()
#time.sleep(3)
#myGame.drawVertical()
#time.sleep(3)
time.sleep(1)

while (True):
    myScreenshot = newScreenshot(myGame) #Use PIL's instead?
    #myGame.updateBoard()
    if myGame.playing() and not keyboard.is_pressed('q'):
      myGame.run()
    else:
        break
    #time.sleep(0.005)


