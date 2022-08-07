
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



def main():
    if 'count' not in st.session_state:
        st.session_state.count = 0
        st.session_state.feedList = []
        st.session_state.results = {}
        st.session_state.positive = 0
        st.session_state.neutral = 0
        st.session_state.negative = 0


        st.session_state.trigger = 0

        st.session_state.count += 1

    goodList = apiGood()
    badList = apiBad()

    st.image("https://aedv.es/wp-content/uploads/2020/06/encuesta-aedv-1024x512.jpg")

    st.title("Feedback Calculator")

    if st.session_state.count != 0:
        tab1, tab2 = st.tabs(["Import Data", "Results"])
        with tab1:
            st.header("Import Data")
            # upload text
            text = st.text_area("Single Feedback")
            # upload csv
            data = st.file_uploader("Multiple Feedback", type="csv")

            if data is not None or text is not None:


                if st.button("Add"):
                    st.session_state.trigger = 1


                    if data is not None:

                        df = pd.read_csv(data, sep=';')
                        list = df.values.tolist()

                        for i in range(len(list)):
                            st.session_state.feedList.append(unidecode(list[i][0]))
                        data = None
                    else:
                        st.session_state.feedList.append(unidecode(text))
                        text = None


                    if st.session_state.trigger == 1:
                        st.success("Feedback Added!")
                        time.sleep(5)
                        st.session_state.trigger = 0


        with tab2:
            st.header("Results")




            if data is not None or text is not None:

                if st.button("Check Results"):
                    my_bar = st.progress(0)

                    st.session_state.trigger = 1

                    i = 1
                    for feed in st.session_state.feedList:
                        goodScore = getGoodMatch(feed, goodList)
                        badScore = getBadMatch(feed, badList)
                        finalScore = goodScore[0] - badScore[0]
                        st.session_state.results[i] = [feed, finalScore]
                        i = i + 1


                    results = getSimpleResult(st.session_state.results)
                    data = listSplit(results)

                    df = pd.DataFrame({"Feedback": st.session_state.feedList, "Score": data[0], "Result": data[1]})
                    df.to_excel("results.xlsx")



                    oldPositive = st.session_state.positive
                    oldNeutral = st.session_state.neutral
                    oldNegative = st.session_state.negative

                    st.session_state.positive = df[df["Score"] > 30].count()[0]
                    st.session_state.negative = df[df["Score"] < 30].count()[0]
                    st.session_state.neutral = (df.count()[0])-(st.session_state.positive+st.session_state.negative)

                    st.subheader("Totals")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Positives", st.session_state.positive, st.session_state.positive - oldPositive)
                    col2.metric("Neutral", st.session_state.neutral, st.session_state.neutral - oldNeutral, delta_color="off")
                    col3.metric("Negatives", st.session_state.negative, st.session_state.negative - oldNegative, delta_color="inverse")

                    for percent_complete in range(100):
                        time.sleep(0.05)
                        my_bar.progress(percent_complete + 1)


                    if st.session_state.trigger == 1:
                        st.success("Feedback Calculated!")
                        st.balloons()
                        time.sleep(5)
                        st.session_state.trigger = 0

                    st.subheader("Result Table")
                    st.table(df)

                    st.subheader("Manage table")
                    with open('results.xlsx', 'rb') as f:
                        st.download_button('Download Table', f,
                                           file_name='results.xlsx')




                    if st.button("Delete input data"):
                        st.session_state.feedList = []
                        text = None
                        data = None
                        my_bar = st.progress(0)
                        for percent_complete in range(100):
                            time.sleep(0.005)
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