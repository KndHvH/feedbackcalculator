
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

st.write("Streamlit version:", st.__version__)

def main():

    feedList = []

    positive = 0
    neutral = 0
    negative = 0

    oldPositive = positive
    oldNeutral = neutral
    oldNegative = negative

    goodList = apiGood()
    badList = apiBad()

    trigger = 0

    st.image("https://aedv.es/wp-content/uploads/2020/06/encuesta-aedv-1024x512.jpg")

    st.title("Feedback Calculator")

    tab1, tab2 = st.tabs(["Import Data", "Results"])
    with tab1:
        st.header("Import Data")
        # upload text
        text = st.text_area("Single Feedback")
        # upload csv
        data = st.file_uploader("Multiple Feedback", type="csv")

        if data is not None or text is not None:


            if st.button("Add"):
                trigger = 1
                my_bar = st.progress(0)


                if data is not None:

                    df = pd.read_csv(data, sep=';')
                    list = df.values.tolist()

                    for i in range(len(list)):
                        feedList.append(unidecode(list[i][0]))
                else:
                    feedList.append(unidecode(text))




                for percent_complete in range(100):
                    time.sleep(0.05)
                    my_bar.progress(percent_complete + 1)

                    if trigger == 1:
                        st.success("Feedback Added!")
                        time.sleep(5)
                        trigger = 0


    with tab2:
        st.header("Results")


        col1, col2, col3 = st.columns(3)
        col1.metric("Positives", positive, positive-oldPositive)
        col2.metric("Neutral", neutral, neutral - oldNeutral,delta_color="off")
        col3.metric("Negatives",negative , negative - oldNegative ,delta_color="inverse")

        if data is not None or text is not None:

            if st.button("Check Results"):
                my_bar = st.progress(0)
                results = {}
                trigger = 1

                i = 1
                for feed in feedList:
                    goodScore = getGoodMatch(feed, goodList)
                    badScore = getBadMatch(feed, badList)
                    finalScore = goodScore[0] - badScore[0]
                    results[i] = [feed, finalScore]
                    i = i + 1


                results = getSimpleResult(results)
                data = listSplit(results)

                df = pd.DataFrame({"Feedback": feedList, "Score": data[0], "Result": data[1]})
                df.to_excel("results.xlsx")



                oldPositive = positive
                oldNeutral = neutral
                oldNegative = negative

                positive = df[df["Score"] > 30].count()[0]
                negative = df[df["Score"] < 30].count()[0]
                neutral = (df.count()[0])-(positive+negative)

                for percent_complete in range(100):
                    time.sleep(0.05)
                    my_bar.progress(percent_complete + 1)


                if trigger == 1:
                    st.success("Feedback Calculated!")
                    st.balloons()
                    time.sleep(5)
                    trigger = 0

                st.subheader("Result Table")
                st.table(df)

                st.subheader("Download Table")
                with open('results.xlsx', 'rb') as f:
                    st.download_button('Download Table', f,
                                       file_name='results.xlsx')




                if st.button("Delete input data"):
                    feedList = []
                    text = None
                    data = None
                    my_bar = st.progress(0)
                    for percent_complete in range(100):
                        time.sleep(0.1)
                        my_bar.progress(percent_complete + 1)








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
            pos
        elif dict[i][1] < -30:
            dict[i] = [dict[i][0],dict[i][1],'bad']

        else:
            dict[i] = [dict[i][0],dict[i][1],'neutral']
    return dict




if __name__ == '__main__':
    main()