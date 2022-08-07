
import streamlit as st
import requests as req
import re
import json
import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from pyngrok import ngrok
from unidecode import unidecode




def main():


    goodList = apiGood()
    badList = apiBad()

    st.markdown("![img.jpg](img.jpg)"
                "# FeedBack calculator")

    tab1, tab2 = st.tabs(["Import Data", "Results"])
    tab1.write("this is tab 1")



    #upload text
    text = st.text_area("Single Feedback")
    #upload csv
    data = st.file_uploader("Multiple Feedback",type="csv")
    tab2.write("this is tab 2")
    st.markdown("# FeedBack calculator")

    clicked = st.button("Click me")

    feedList=[]
    df = pd.read_csv("dataTest.csv",sep=';')
    list=df.values.tolist()

    for i in range(len(list)):
        feedList.append(unidecode(list[i][0]))


    results={}

    i=1
    #score generator
    for feed in feedList:
        goodScore = getGoodMatch(feed,goodList)
        badScore = getBadMatch(feed,badList)
        finalScore = goodScore[0] - badScore[0]
        results[i]=[feed,finalScore]
        i=i+1

    results = getSimpleResult(results)
    data = listSplit(results)


    df = pd.DataFrame({"Feedback": feedList, "Score":data[0],"Result":data[1]})
    df.to_excel("results.xlsx")




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




if __name__ == '__main__':
    main()