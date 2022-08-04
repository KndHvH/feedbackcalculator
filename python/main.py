import streamlit as st
import json
# import re
# from pyngrok import ngrok
from api import *
from match import *
from simpleResult import *

#json api import
goodList = apiGood()
badList = apiBad()


# test.json file import (test only)

userFeed = json.load(open("test.json"))
# print(userFeed['feed'])
userFeed = userFeed['feed']
feedList=[]
for i in userFeed:
    feedList.append(i['feed'])


results={}
i=1
#score generator
for feed in feedList:
    goodScore = getGoodMatch(feed,goodList)
    badScore = getBadMatch(feed,badList)
    finalScore = goodScore[0] - badScore[0]

    results[i]=[feed,finalScore]
    i=i+1

    #test metrics
    # print(feed)
    # print(goodScore)
    # print(badScore)
    # print(finalScore)

results = getSimpleResult(results)
resultsJson = json.dumps(results)
print(resultsJson)