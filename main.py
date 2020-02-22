# regex curly brace
# https://stackoverflow.com/questions/413071/regex-to-get-string-between-curly-braces-i-want-whats-between-the-curly-brace

import praw
import requests
import json
from itertools import zip_longest

reddit = praw.Reddit('bot1')

subreddit = reddit.subreddit("testingground4bots")
#subreddit = reddit.subreddit("destinythegame + sharditkeepit")

HEADERS = {"X-API-KEY": 'my api key'}


base_url = "https://www.bungie.net/Platform/"
item_url = base_url + "Destiny2/Manifest/DestinyInventoryItemDefinition/"
perk_url = base_url + "Destiny2/Manifest/DestinyPlugSetDefinition/"
base_search_url = base_url + "Destiny2/Armory/Search/DestinyInventoryItemDefinition/"

# prints json file, for testing
def printj(obj):
    text = json.dumps(obj.json(), sort_keys=True, indent=4) 
    print(text)




# takes an itemHash and prints out all of the possible perks the corresponding item can roll in each perk column
def printPerks(itemHash):
    returnString = ""

    test_url = item_url + str(itemHash)
    r = requests.get(test_url, headers=HEADERS)

    # makes sure it is a weapon (itemType == 3)
    if (r.json()['Response']['itemType'] != 3):
        return returnString

    itemName = r.json()['Response']['displayProperties']['name']

    # fills out perkSetHashList with a list of hashes corresponding to perk sets
    # works for y2 random rolls, y2 static rolls, y1 static rolls, exotics w/o catalyst, exotics w catalyst
    i=0
    perkSetHashList = []
    for socket in r.json()['Response']['sockets']['socketEntries']:
        if i==5:
            break
        try:
            perkSetHashList.append(socket['randomizedPlugSetHash'])
        except KeyError:
            try:
                perkSetHashList.append(socket['reusablePlugSetHash'])
            except KeyError:
                break
        i+=1
        #print(perkSetHashList[i])


    # go through each element in each perk set hash
    # put it into a multidimensional array
    output = []
    for perkSetHash in perkSetHashList:
        line = []

        r = requests.get(perk_url + str(perkSetHash), headers=HEADERS)

        for perk in r.json()['Response']['reusablePlugItems']:
            perkHash = perk['plugItemHash']
            r1 = requests.get(item_url + str(perkHash), headers=HEADERS)
            name = r1.json()['Response']['displayProperties']['name']
            line.append(name)
            print(name)
            
        output.append(line)
        #print(len(output))
    
    #print(output)
    #output array into reddit formatting
    numColumns = len(output)
    new_output = list(zip_longest(*output, fillvalue=" "))
    #print("len(new_output)): " + str(len(new_output)))
    #print(new_output)

    returnString += itemName + "\n-\n"

    heading1 = "Column 1|Column 2|Column 3|Column 4"
    heading2 = ":--|:--|:--|:--"
    if numColumns == 5:
        heading1 += "|Column 5"
        heading2 += "|:--"
    returnString += heading1 + "\n"
    returnString += heading2 + "\n"

    for line in new_output:
        tableLine = ""
        for name in line:
            tableLine = tableLine + name + "|"
        tableLine = tableLine[:-1]                      #slice off the last '|'
        returnString += tableLine + "\n"

    return returnString


def searchCurlyBrace(comment):
    searchTerm = None
    text = comment.body
    lbrace = text.find('{')
    rbrace = text.find('}')
    if lbrace != -1 and rbrace != -1:
        searchTerm = text[lbrace+1:rbrace]
    return searchTerm

def main():
    for comment in subreddit.stream.comments(skip_existing=True):
        search_term = searchCurlyBrace(comment)
        if search_term is not None:
            #comment.reply("Searching for: " + search_term)
            search_url = base_search_url + search_term

            r = requests.get(search_url, headers=HEADERS)
            numResults = r.json()['Response']['results']['totalResults']
            #print("numResults: " + str(numResults))
            for i in range(numResults):
                itemHash = r.json()['Response']['results']['results'][i]['hash']
                #print("itemHash: " + str(itemHash))
                printString = printPerks(itemHash)
                if printString != "":
                    comment.reply(printString)

main()
    


