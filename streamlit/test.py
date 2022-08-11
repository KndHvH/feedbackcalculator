import streamlit as st
import requests as req
import re
import json
import pandas as pd
import time
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from pyngrok import ngrok
from unidecode import unidecode
from PIL import Image

def apiGood():
    goodList=[]
    apiData = req.get("https://kndhvh.github.io/good.json")
    good = apiData.json()['good']
    for i in good:
        goodList.append(i['good'])
    return goodList

def apiBad():
    badList=[]
    apiData = req.get("https://kndhvh.github.io/bad.json")
    bad = apiData.json()['bad']
    for i in bad:
        badList.append(i['bad'])
    return badList

def listSplit(dict):
    scoreList=[]
    resultList=[]
    for i in dict:
        scoreList.append(dict[i][1])
        resultList.append(dict[i][2])
    return scoreList,resultList

def getGoodMatch(input,goodList):
    matchScore = process.extract(input,goodList,scorer=fuzz.token_set_ratio)
    totalScore = 0
    for i in range(0,3):
        totalScore += matchScore[i][1]
    return totalScore,matchScore

def getBadMatch(input,badList):
    matchScore = process.extract(input,badList,scorer=fuzz.token_set_ratio)
    totalScore = 0
    for i in range(0,3):
        totalScore += matchScore[i][1]
    return totalScore,matchScore

def getSimpleResult(dict):
    for i in dict:
        if dict[i][1] > 30:
            dict[i] = [dict[i][0],dict[i][1],'good']
        elif dict[i][1] < -30:
            dict[i] = [dict[i][0],dict[i][1],'bad']
        else:
            dict[i] = [dict[i][0],dict[i][1],'neutral']
    return dict

goodList = apiGood()
badList = apiBad()

list = ["ola"]
result=[]

if list != []:
    i = 1
    for feed in list:
        print(feed)
        goodScore = getGoodMatch(feed, goodList)
        badScore = getBadMatch(feed, badList)
        print("god",goodScore)
        print("bad",badScore)
        finalScore = goodScore[0] - badScore[0]
        print("final", finalScore)
        result[i] = [feed, finalScore]
        print("list el", result[i])
        i = i + 1

    results = getSimpleResult(result)
    print(results)
    data = listSplit(results)
    print(data)

    st.session_state.df = pd.DataFrame({"Feedback": st.session_state.feedList, "Score": data[0], "Result": data[1]})
    st.session_state.df.to_excel("results.xlsx")