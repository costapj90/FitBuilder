#################################################
# FitBuilder v3.2
#
# Patrick C
# pcosta
#################################################
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import random
from cmu_112_graphics import *

print()
print('Running...')
print('––––––––––––––––')
#########################################################################

#All help with using aspects/modules of beautifulsoup were adapted from information listed
#on the official documentation website: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

#########################################################################
#helper functions:

#helper function that returns the image links for each piece within an outfit list
def getPhotos(fitList):
    imgLinkList = []
    for (name, link, price) in fitList:
        htmlSource = requests.get(link).text
        soup = BeautifulSoup(htmlSource, 'lxml')
        result = soup.find_all('img')
        newRes = str(result).split('srcset="')[1].split(' 640w')[0]
        imgLinkList.append(newRes)
    return imgLinkList

#helper function that returns the total number of unique clothing items (regardless of color) within an input dictionary
def getLength(clothingDict):
    wholeList = list(clothingDict.values())
    totalCount = 0
    for piece in wholeList:
        for color in piece:
            totalCount +=1
    return totalCount

#primary helper function that returns a random top, pants, and shoes from a given dictionaries for each item and color
def inputFitBuilder(topDict, pantDict, shoeDict):
    fitList = []
    fullTopList = []
    for name in topDict:
        for (color, link, price) in topDict[name]:
            fullTopList.append((name, link, price))
    fullPantList = []
    for name in pantDict:
        for (color, link, price) in pantDict[name]:
            fullPantList.append((name, link, price))
    fullShoeList = []
    for name in shoeDict:
        for (color, link, price) in shoeDict[name]:
            fullShoeList.append((name, link, price))
    fitList.append(random.choice(fullTopList))
    fitList.append(random.choice(fullPantList))
    fitList.append(random.choice(fullShoeList))
    return fitList

#helper function that returns the full html soup for the link generated based on color input for each clothing piece
def ENDSoupListBuilder(baseLink):
    htmlSource1 = requests.get(baseLink + '1').text
    soupPg1 = BeautifulSoup(htmlSource1, 'lxml')
    fullCount = int((soupPg1.find('div', class_='sc-14b11kg-3 imDHMD').text).split(" ")[0])
    runtimeModifier = 1 #lower value -> higher runtime to build dicts, but more clothing choices
    pageCount = (fullCount//(runtimeModifier*120))+2
    fullSoupList = []
    for pageNum in range(1, pageCount):
        htmlSource = requests.get(baseLink + str(pageNum)).text
        soup = BeautifulSoup(htmlSource, 'lxml')
        fullSoupList.append(soup)
    return fullSoupList 

#helper function that builds full dictionaries for each input link soup
def ENDPageDictBuildHelper(soup, fullDict):
    nameList = []
    colorList = []
    priceList = []
    itemLinkList = []
    for name in soup.find_all('span', class_='sc-zofufr-3 izFyzC'):
        nameList.append(str(name.text))
    for color in soup.find_all('span', class_='sc-zofufr-4 cRTnNY'):
        colorList.append(str(color.text))
    for price in soup.find_all("div", class_="sc-zofufr-5 jbiknW"):
        priceList.append(str(price.text))
    for price2 in soup.find_all("div", class_="sc-zofufr-5 cVPgMh"):
        thisPrice2 = '$' + price2.text.split('$')[1]
        priceList.append(str(thisPrice2))
    for a in soup.find_all('a', class_='sc-e4qf6g-0 giHZdR sc-zofufr-2 caFgJe'):
        fullLink = str('https://www.endclothing.com/' + a['href'])
        itemLinkList.append(fullLink)
    for i in range(len(nameList)):
        name = nameList[i]
        color = colorList[i]
        thisLink = itemLinkList[i]
        price = priceList[i]
        if name not in fullDict:
            fullDict[name] = {(color, thisLink, price)}
        else:
            fullDict[name].add((color, thisLink, price)) 
    return fullDict

#primary helper function that uses ENDPageDictBuildHelper to ultimately create each full clothing piece dictionary
def ENDFullDictBuilder(fullSoupList, fullDict):
    for soup in fullSoupList:
        ENDPageDictBuildHelper(soup, fullDict)
    return fullDict

#function that opens the tabs of the current items within a selenium chrome browser
def openTabs(fitList):
    #ENTER THE DIRECTORY TO YOUR CHROMEDRIVER FOLDER EXECUTABLE HERE v v v
    driver = webdriver.Chrome('/Users/pcosta/Desktop/ChromeD/chromedriver')
    topUrl = fitList[0][1]
    pantUrl = fitList[1][1]
    shoeUrl = fitList[2][1]
    #The following 7 lines of code for opening multiple tabs within a selenium browser taken from the following link
    #https://stackoverflow.com/questions/39281806/python-opening-multiple-tabs-using-selenium
    driver.get(topUrl)
    driver.execute_script("window.open('about:blank', 'tab2');")
    driver.switch_to.window("tab2")
    driver.get(pantUrl)
    driver.execute_script("window.open('about:blank', 'tab3');")
    driver.switch_to.window("tab3")
    driver.get(shoeUrl)

#main function that runs the current outfit through a number of unique tests to check color compatability
def fitCheckerMain(topLink, pantLink, shoeLink):
    topUnique = uniqueHelper(topLink)
    pantUnique = uniqueHelper(pantLink)
    shoeUnique = uniqueHelper(shoeLink)
    baseCheck = [len(topUnique) < 5000, len(pantUnique) < 5000, len(shoeUnique) < 5000]
    #If enough items are grayscale, outfit cannot have too many clashing pieces -> is fashionable by FitBuilder's standards
    if baseCheck.count(True) >= 2:
        return 'Outfit passes! \nOver half of the items are near-grayscale.'
    #If too many colors are present, outfit pieces will clash
    elif True not in baseCheck:
        return 'Outfit fails! \nThere are too many colors present.\n–––\nHint: Try to have at least one near-grayscale item present.'
    else:
        print()
        #main statements to help return certain result statements based on adjacent and complement color checkers
        if True not in [baseCheck[0], baseCheck[1]]:
            print('checking top and pants...')
            adjResults = (adjChecker(topUnique, pantUnique))
            if adjResults[0] == True:
                return adjResults[1]
            compResults = (compChecker(topUnique, pantUnique))
            if compResults[0] == True:
                return compResults[1]
        elif True not in [baseCheck[1], baseCheck[2]]:
            print('checking pants and shoes...')
            adjResults = (adjChecker(pantUnique, shoeUnique))
            if adjResults[0] == True:
                return adjResults[1]
            compResults = (compChecker(pantUnique, shoeUnique))
            if compResults[0] == True:
                return compResults[1]
        elif True not in [baseCheck[0], baseCheck[2]]:
            print('checking top and shoes...')
            adjResults = (adjChecker(topUnique, shoeUnique))
            if adjResults[0] == True:
                return adjResults[1]
            compResults = (compChecker(topUnique, shoeUnique))
            if compResults[0] == True:
                return compResults[1]
        if adjResults[2] >= compResults[2]:
            return adjResults[1]
        else:
            return compResults[1]

#helper function to return the list of pixels within an image that are determined to be 'non-grayscale'
def uniqueHelper(url):
    #The following 3 lines of code for getting the pixel RGBs in an image RGB values used from the PIL documentation:
    #https://pillow.readthedocs.io/en/stable/
    thisImg = Image.open(requests.get(url, stream=True).raw).convert('RGB')
    width, height = thisImg.size
    pix = thisImg.load()
    fullList = []
    for i in range(width):
        for j in range(height):
            (r,g,b) = pix[i,j]
            fullList.append((r,g,b))
    commonUnique = []
    for i in range(len(fullList)):
        r = fullList[i][0] 
        g = fullList[i][1]
        b = fullList[i][2]
        #distance needed between rgb values to be non-grayscale
        val = 30
        if ((abs(r-g) > val and abs(r-b) > val) or
            (abs(r-g) > val and abs(b-g) > val) or 
            (abs(b-g) > val and abs(r-b) > val)):
            commonUnique.append((r,g,b))
    return commonUnique

#main function to test if adjacent colors are present in both pieces
def adjChecker(piece1Unique, piece2Unique, recMin=7.5):
    piece1Set = set(piece1Unique)
    fullFound = []
    #scans rgb values around the values of those in piece2 and comapares to the pixels in piece1
    for pixl in piece2Unique:
        for i in range(-30,30,1):
            if (pixl[0]+i,pixl[1],pixl[2]) in piece1Set:
                fullFound.append((pixl[0]+i,pixl[1],pixl[2]))
                piece1Set.remove((pixl[0]+i,pixl[1],pixl[2]))
                break
            elif (pixl[0],pixl[1]+i,pixl[2]) in piece1Set:
                fullFound.append((pixl[0],pixl[1]+i,pixl[2]))
                piece1Set.remove((pixl[0],pixl[1]+i,pixl[2]))
                break
            elif (pixl[0],pixl[1],pixl[2]+i) in piece1Set:
                fullFound.append((pixl[0],pixl[1],pixl[2]+i))
                piece1Set.remove((pixl[0],pixl[1],pixl[2]+i))
                break
            elif (pixl[0]+i,pixl[1]+i,pixl[2]) in piece1Set:
                fullFound.append((pixl[0]+i,pixl[1]+i,pixl[2]))
                piece1Set.remove((pixl[0]+i,pixl[1]+i,pixl[2]))
                break
            elif (pixl[0],pixl[1]+i,pixl[2]+i) in piece1Set:
                fullFound.append((pixl[0],pixl[1]+i,pixl[2]+i))
                piece1Set.remove((pixl[0],pixl[1]+i,pixl[2]+i))
                break
            elif (pixl[0]+i,pixl[1]+i,pixl[2]+i) in piece1Set:
                fullFound.append((pixl[0]+i,pixl[1]+i,pixl[2]+i))
                piece1Set.remove((pixl[0]+i,pixl[1]+i,pixl[2]+i))
                break
    thisPercent = ((len(fullFound)/len(piece2Unique))*100)
    print("matched adj percent :", thisPercent)
    #creates return strings based on percent results
    if thisPercent >= recMin:
        return (True, f'Outfit passes! \nThere are enough adjacent colors present.\nYour outfit\'s match value is {round((thisPercent-recMin), 2)}% above the \nrecommended adjacent minimum of {recMin}%.')
    else:
        return (False, f"Outfit fails! \nThe colors present are not adjacent enough.\nYour outfit\'s match value is {round((recMin-thisPercent), 2)}% below the \nrecommended adjacent minimum of {recMin}%.\n–––\nHint: Use a color wheel to compare pieces!", thisPercent/recMin)

#main function to test if complementary colors are present in both pieces
def compChecker(piece1Unique, piece2Unique, recMin=3):
    piece1Set = set(piece1Unique)
    piece2Complement = []
    for (r,g,b) in piece2Unique:
        #The following 3 lines of code for determining the complement of a set of RGB values taken from this SO post:
        #https://stackoverflow.com/questions/3054873/programmatically-find-complement-of-colors
        r2 = max(r,g,b) + min(r,g,b) - r
        g2 = max(r,g,b) + min(r,g,b) - g   
        b2 = max(r,g,b) + min(r,g,b) - b
        piece2Complement.append((r2,g2,b2))
    fullFound = []
    #scans rgb values around the values of those in piece2's complement and comapares to the pixels in piece1
    for pixl in piece2Complement:
        for i in range(-30,30,1):
            if (pixl[0]+i,pixl[1],pixl[2]) in piece1Set:
                fullFound.append((pixl[0]+i,pixl[1],pixl[2]))
                piece1Set.remove((pixl[0]+i,pixl[1],pixl[2]))
                break
            elif (pixl[0],pixl[1]+i,pixl[2]) in piece1Set:
                fullFound.append((pixl[0],pixl[1]+i,pixl[2]))
                piece1Set.remove((pixl[0],pixl[1]+i,pixl[2]))
                break
            elif (pixl[0],pixl[1],pixl[2]+i) in piece1Set:
                fullFound.append((pixl[0],pixl[1],pixl[2]+i))
                piece1Set.remove((pixl[0],pixl[1],pixl[2]+i))
                break
            elif (pixl[0]+i,pixl[1]+i,pixl[2]) in piece1Set:
                fullFound.append((pixl[0]+i,pixl[1]+i,pixl[2]))
                piece1Set.remove((pixl[0]+i,pixl[1]+i,pixl[2]))
                break
            elif (pixl[0],pixl[1]+i,pixl[2]+i) in piece1Set:
                fullFound.append((pixl[0],pixl[1]+i,pixl[2]+i))
                piece1Set.remove((pixl[0],pixl[1]+i,pixl[2]+i))
                break
            elif (pixl[0]+i,pixl[1]+i,pixl[2]+i) in piece1Set:
                fullFound.append((pixl[0]+i,pixl[1]+i,pixl[2]+i))
                piece1Set.remove((pixl[0]+i,pixl[1]+i,pixl[2]+i))
                break
    thisPercent = ((len(fullFound)/len(piece2Unique))*100)
    print("matched comp percent :", thisPercent)
    #creates return strings based on percent results
    if thisPercent >= recMin:
        return (True, f'Outfit passes! \nThere are enough complementary colors present.\nYour outfit\'s match value is {round((thisPercent-recMin), 2)}% above the \nrecommended complement minimum of {recMin}%.')
    else:
        return (False, f"Outfit fails! \nThe colors present are not complementary enough.\nYour outfit\'s match value is {round((recMin-thisPercent), 2)}% below the \nrecommended complement minimum of {recMin}%.\n–––\nHint: Use a color wheel to compare pieces!", thisPercent/recMin)
    
######################################################################### 
#main app class:

class FitBuilder(App):
    #function for initializing variables of class instance
    def appStarted(self):
        self.colorList = ['Blue','Green','Yellow','Orange','Red','Pink','Purple','White','Grey','Black']
        self.imgList = []
        self.baseFitList = []
        self.isLoading = False
        self.inItemScreen = False
        self.inHomeScreen = True
        self.inTopScreen = False
        self.inPantScreen = False
        self.inShoeScreen = False
        self.inResultScreen = False
        self.currTopColor = ''
        self.topDict = dict()
        self.currPantColor = ''
        self.pantDict = dict()
        self.currShoeColor = ''
        self.shoeDict = dict()
        self.resultMessage = '-> TEMP'
        self.topSwitchCx = 500
        self.topSwitchCy = 195+25
        self.pantSwitchCx = 500
        self.pantSwitchCy = 485+25
        self.shoeSwitchCx = 500
        self.shoeSwitchCy = 735+25
        self.menuButtonCx = 100
        self.menuButtonCy = 30
        self.doneButtonCx = self.width-100
        self.doneButtonCy = 30
        self.backButtonCx = 142.5
        self.backButtonCy = 475
        self.openButtonCx = 142.5
        self.openButtonCy = 525

    #main function to create dictionary of tops based on input color
    def topDictBuilder(self):
        topinputColor = self.currTopColor
        print('top color:', self.currTopColor)
        #custom link based on input color
        baseTopLink = f'https://www.endclothing.com/us/clothing/sweats-and-hoods?colour={topinputColor}&page='
        topSoupList = ENDSoupListBuilder(baseTopLink)
        topDict = ENDFullDictBuilder(topSoupList, {})
        totalTops = getLength(topDict)
        print('topDict size:', totalTops)
        return topDict

    #main function to create dictionary of pants based on input color
    def pantDictBuilder(self):
        pantinputColor = self.currPantColor
        print('pant color:', self.currPantColor)
        basePantLink = f'https://www.endclothing.com/us/clothing/trousers?colour={pantinputColor}&page='
        pantSoupList = ENDSoupListBuilder(basePantLink)
        pantDict = ENDFullDictBuilder(pantSoupList, {})
        totalPants = getLength(pantDict)
        print('pantDict size:', totalPants)
        return pantDict

    #main function to create dictionary of shoes based on input color
    def shoeDictBuilder(self):
        shoeinputColor = self.currShoeColor
        print('shoe color:', self.currShoeColor)
        baseShoesLink = f'https://www.endclothing.com/us/footwear/sneakers?colour={shoeinputColor}&page='
        shoeSoupList = ENDSoupListBuilder(baseShoesLink)
        shoeDict = ENDFullDictBuilder(shoeSoupList, {})
        totalShoes = getLength(shoeDict)
        print('shoeDict size:', totalShoes)
        return shoeDict

    #updates displayed images based on self.imgList
    def imageRebuilder(self):
        #the following 6 lines of image implementation adapted from notes on 112 course website:
        #https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#loadImageUsingUrl
        self.topImg = self.loadImage(self.imgList[0])
        self.topImg = self.scaleImage(self.topImg, 1/4.3)
        self.pantImg = self.loadImage(self.imgList[1])
        self.pantImg = self.scaleImage(self.pantImg, 1/4)
        self.shoeImg = self.loadImage(self.imgList[2])
        self.shoeImg = self.scaleImage(self.shoeImg, 1/4.8)

    #main function to interpret key inputs
    def keyPressed(self, event):
        if (event.key) == 'q':
            self.inHomeScreen = False
            self.inTopScreen = True
        #following three if/elif statements used to record user's desired input color
        if (event.key) in '1234567890' and self.inTopScreen:
            self.currTopColor = self.colorList[int(event.key)]
            self.topDict = FitBuilder.topDictBuilder(self)
            if len(self.topDict) > 0:
                print("in pants screen")
                self.inTopScreen = False
                self.inPantScreen = True
            else:
                print('ERR: No items of that color in this category. Pick a new color.')          
        elif (event.key) in '1234567890' and self.inPantScreen:
            self.currPantColor = self.colorList[int(event.key)]
            self.pantDict = FitBuilder.pantDictBuilder(self)
            if len(self.pantDict) > 0:
                self.inPantScreen = False
                self.inShoeScreen = True
            else:
                print('ERR: No items of that color in this category. Pick a new color.')
        elif (event.key) in '1234567890' and self.inShoeScreen:
            self.currShoeColor = self.colorList[int(event.key)]
            self.shoeDict = FitBuilder.shoeDictBuilder(self)
            if len(self.shoeDict) > 0:
                self.baseFitList = inputFitBuilder(self.topDict, self.pantDict, self.shoeDict)
                self.imgList = getPhotos(self.baseFitList)
                FitBuilder.imageRebuilder(self)
                self.inShoeScreen = False
                self.inItemScreen = True
            else:
                print('ERR: No items of that color in this category. Pick a new color.')

    #main function to interpret mouse clicks
    def mousePressed(self, event):
        tcx, tcy = self.topSwitchCx, self.topSwitchCy
        pcx, pcy = self.pantSwitchCx, self.pantSwitchCy
        scx, scy = self.shoeSwitchCx, self.shoeSwitchCy
        mcx, mcy = self.menuButtonCx, self.menuButtonCy
        dcx, dcy = self.doneButtonCx, self.doneButtonCy
        bcx, bcy = self.backButtonCx, self.backButtonCy
        ocx, ocy = self.openButtonCx, self.openButtonCy
        if self.inItemScreen:
            if ((tcx-100 <= event.x <= tcx+100) and (tcy-20 <= event.y <= tcy+20)):
                newTop = inputFitBuilder(self.topDict, self.pantDict, self.shoeDict)
                newImgList = getPhotos(newTop)
                self.baseFitList[0] = newTop[0]
                self.imgList[0] = newImgList[0]
                #updates image when button is clicked
                FitBuilder.imageRebuilder(self)
            elif ((pcx-100 <= event.x <= pcx+100) and (pcy-20 <= event.y <= pcy+20)):
                newPants = inputFitBuilder(self.topDict, self.pantDict, self.shoeDict)
                newImgList = getPhotos(newPants)
                self.baseFitList[1] = newPants[1]
                self.imgList[1] = newImgList[1]
                FitBuilder.imageRebuilder(self)
            elif ((scx-100 <= event.x <= scx+100) and (scy-20 <= event.y <= scy+20)):
                newShoes = inputFitBuilder(self.topDict, self.pantDict, self.shoeDict)
                newImgList = getPhotos(newShoes)
                self.baseFitList[2] = newShoes[2]
                self.imgList[2] = newImgList[2]
                FitBuilder.imageRebuilder(self)
            elif ((mcx-65 <= event.x <= mcx+65) and (mcy-20 <= event.y <= mcy+20)):
                self.inTopScreen = True
                self.inItemScreen = False
            elif ((dcx-65 <= event.x <= dcx+65) and (dcy-20 <= event.y <= dcy+20)):
                self.inItemScreen = False
                self.inResultScreen = True
                topLink = self.imgList[0]
                pantLink = self.imgList[1]
                shoeLink = self.imgList[2]
                self.resultMessage = fitCheckerMain(topLink, pantLink, shoeLink)
        elif self.inResultScreen:
            if ((bcx-100 <= event.x <= bcx+100) and (bcy-20 <= event.y <= bcy+20)):
                self.inResultScreen = False
                self.inItemScreen = True
            if ((ocx-100 <= event.x <= ocx+100) and (ocy-20 <= event.y <= ocy+20)):
                openTabs(self.baseFitList)

    #creates the item screen window
    def drawItemScreen(self, canvas):
        tcx, tcy = self.topSwitchCx, self.topSwitchCy
        pcx, pcy = self.pantSwitchCx, self.pantSwitchCy
        scx, scy = self.shoeSwitchCx, self.shoeSwitchCy
        mcx, mcy = self.menuButtonCx, self.menuButtonCy
        dcx, dcy = self.doneButtonCx, self.doneButtonCy
        canvas.create_image(200, 195, image=ImageTk.PhotoImage(self.topImg))
        canvas.create_image(200, 705, image=ImageTk.PhotoImage(self.shoeImg))
        canvas.create_image(200, 485, image=ImageTk.PhotoImage(self.pantImg))
        canvas.create_rectangle(tcx-100, tcy-20, tcx+100, tcy+20, fill='#D3D3D3')
        canvas.create_text(tcx, tcy, text=f'Change top ({self.currTopColor})', fill='black')
        canvas.create_rectangle(pcx-100, pcy-20, pcx+100, pcy+20, fill='#D3D3D3')
        canvas.create_text(pcx, pcy, text=f'Change bottoms ({self.currPantColor})', fill='black')
        canvas.create_rectangle(scx-100, scy-20, scx+100, scy+20, fill='#D3D3D3')
        canvas.create_text(scx, scy, text=f'Change shoes ({self.currShoeColor})', fill='black')
        canvas.create_line(30,330,self.width-30,330, width=5,fill='#929496')
        canvas.create_line(30,637,self.width-30,637, width=5,fill='#929496')
        canvas.create_text(400, self.topSwitchCy-60, text=f'{self.baseFitList[0][0]}', font=f'Arial {560//len(self.baseFitList[0][0])} bold', anchor = 'sw', fill='black')
        canvas.create_text(400, self.topSwitchCy-30, text=f'{self.baseFitList[0][2]}', font=f'Arial 20 bold', anchor = 'sw',fill='#929496')
        canvas.create_line(385,self.topSwitchCy+15, 385, self.topSwitchCy-75, fill='#929496', width=4)
        canvas.create_text(400, self.pantSwitchCy-60, text=f'{self.baseFitList[1][0]}', font=f'Arial {560//len(self.baseFitList[1][0])} bold', anchor = 'sw', fill='black')
        canvas.create_text(400, self.pantSwitchCy-30, text=f'{self.baseFitList[1][2]}', font=f'Arial 20 bold', anchor = 'sw',fill='#929496')
        canvas.create_line(385,self.pantSwitchCy+15, 385, self.pantSwitchCy-75, fill='#929496', width=5)
        canvas.create_text(400, self.shoeSwitchCy-60, text=f'{self.baseFitList[2][0]}', font=f'Arial {560//len(self.baseFitList[2][0])} bold', anchor = 'sw', fill='black')
        canvas.create_text(400, self.shoeSwitchCy-30, text=f'{self.baseFitList[2][2]}', font=f'Arial 20 bold', anchor = 'sw',fill='#929496')
        canvas.create_line(385,self.shoeSwitchCy+15, 385, self.shoeSwitchCy-75, fill='#929496', width=5)
        canvas.create_rectangle(mcx-65, mcy-20, mcx+65, mcy+20, fill='#D3D3D3')
        canvas.create_text(mcx, mcy, text='Repick Colors', fill='black')
        canvas.create_rectangle(dcx-65, dcy-20, dcx+65, dcy+20, fill='#D3D3D3')
        canvas.create_text(dcx, dcy, text='Check Outfit', fill='black')

    def drawHomeScreen(self,canvas):
        canvas.create_text(self.width//2, self.height//2-25, text='FitBuilder.', font='Arial 60 bold', fill='black')
        canvas.create_text(self.width//2, self.height//2+50, text='Press Q to begin!', font='Arial 20 bold', fill='black')

    #color table used in all user color input screens
    def drawColorPickTable(self,canvas):
        for i in range(len(self.colorList)):
            cx, cy = 100 + (i*60), 400
            canvas.create_rectangle(cx + 30, cy+30, cx-30, cy-30, fill=self.colorList[i])
            canvas.create_text(cx, cy + 60, text=i, font='Arial 25 bold', fill='black')
    
    def drawTopColorPick(self,canvas):
        canvas.create_text(self.width//2, self.height//2-75, 
                            text='Press a number key to pick a top color', font='Arial 30 bold', fill='black')
        FitBuilder.drawColorPickTable(self, canvas)

    def drawPantColorPick(self,canvas):
        canvas.create_text(self.width//2, self.height//2-75, 
                            text='Press a number key to pick a pant color', font='Arial 30 bold', fill='black')
        FitBuilder.drawColorPickTable(self, canvas)

    def drawShoeColorPick(self, canvas):
        canvas.create_text(self.width//2, self.height//2-75, 
                            text='Press a number key to pick a shoe color', font='Arial 30 bold', fill='black')
        FitBuilder.drawColorPickTable(self, canvas)

    def drawResultScreen(self, canvas):
        bcx, bcy = self.backButtonCx, self.backButtonCy
        ocx, ocy = self.openButtonCx, self.openButtonCy
        canvas.create_text(150, 200, text='Results:',font='Arial 56 bold', fill='black')
        canvas.create_line(42.5,235,300,235, width=5)
        canvas.create_text(42.5, 275, text=self.resultMessage, font='Arial 24 bold', anchor='nw', fill='black')
        canvas.create_rectangle(bcx-100, bcy-20, bcx+100, bcy+20, fill='#D3D3D3')
        canvas.create_text(bcx, bcy, text='Go Back', fill='black')
        canvas.create_rectangle(ocx-100, ocy-20, ocx+100, ocy+20, fill='#D3D3D3')
        canvas.create_text(ocx, ocy, text='Open Items', fill='black')
        totalPrice = int(self.baseFitList[0][2][1:]) + int(self.baseFitList[1][2][1:]) + int(self.baseFitList[2][2][1:])
        canvas.create_text(ocx+115,ocy,text=f'(Total price: ${totalPrice})', font='Arial 18 bold', anchor='w', fill='black')

    def redrawAll(self, canvas):
        if self.inHomeScreen:
            FitBuilder.drawHomeScreen(self,canvas)
        else:
            if self.inItemScreen:
                FitBuilder.drawItemScreen(self,canvas)
            elif self.inTopScreen:
                FitBuilder.drawTopColorPick(self,canvas)
            elif self.inPantScreen:
                FitBuilder.drawPantColorPick(self, canvas)
            elif self.inShoeScreen:
                FitBuilder.drawShoeColorPick(self, canvas)
            elif self.inResultScreen:
                FitBuilder.drawResultScreen(self, canvas)
            canvas.create_text(self.width//2, 30, text='FitBuilder.', font='Arial 48 bold', fill='black')
            canvas.create_line(0,60,self.width,60, width=5,fill='black')

#########################################################################

FitBuilder(width=750, height=800)

#########################################################################
print('––––––––––––––––')
print('...Complete.')


        


