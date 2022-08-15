import random

import streamlit as st
import requests as req
import re
import json
import pandas as pd
import time
import matplotlib.pyplot as plt
from random import randrange
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from pyngrok import ngrok
from unidecode import unidecode
from PIL import Image
import seaborn as sns


#dashboard version


def main():


    # declarando variaveis utilizando session state (tem uma forma melhor de fazer isso)
    if 'feedList' not in st.session_state:
        # variavel para armazenar todos os feedbacks inputados
        st.session_state.feedList = []
    if 'results' not in st.session_state:
        # variavel para armazenar os resultados calculados
        st.session_state.results = {}
    if 'positive' not in st.session_state:
        # contagem de positivos
        st.session_state.positive = 0
    if 'total' not in st.session_state:
        # contagem total
        st.session_state.total = 0
    if 'neutral' not in st.session_state:
        # contagem de neutros
        st.session_state.neutral = 0
    if 'negative' not in st.session_state:
        # contagem de negativos
        st.session_state.negative = 0
    if 'df' not in st.session_state:
        # dataframe para o display e download dos resultados
        st.session_state.df = pd.DataFrame(st.session_state.feedList)

    #importando as 2 apis para o fuzzy comparar
    goodList = apiGood()
    badList = apiBad()

    # titulo e foto do site
    st.image("https://aedv.es/wp-content/uploads/2020/06/encuesta-aedv-1024x512.jpg",width=395)
    st.title("Feedback Calculator")

    # divisao de 3 paginas, sendo para importar os dados, ver os resultados e um tutorial de como usar o site
    tab1, tab2 , tab3= st.tabs(["Import Data", "Results","Tutorial"])
    with tab1:
        st.header("Import Data")
        # feature para usuario fazer upload manual(escrever o feedback)
        text = st.text_area("Single Feedback")

        # feature para usuario fazer upload em csv
        csv = st.file_uploader("Multiple Feedback", type="csv")

        # true se o usuario fizer o upload de um csv
        if csv is not None:
            # e apertar o botao
            if st.button("Add"):
                # le o csv e armazena em um df, depois converte para uma lista
                idf = pd.read_csv(csv, sep=';')
                list = idf.values.tolist()

                # para cada i no tamanho da lista, da um append na lista de feedbacks totais
                for i in range(len(list)):
                    st.session_state.feedList.append(unidecode(list[i][0]))

                # apos o procedimento esvazia o input para nao ter dados duplicados
                csv = None

                st.success("Feedback Added!")
                time.sleep(3)
                st.experimental_rerun()

        # true se o usuario fizer um upload manual (elif para o usuario poder trabalhar com os dois campos simultaniamente
        # sem dados duplicados)
        elif text != "":
            if st.button("Add"):
                # append na lista de feedbacks totais com o texto inserido
                st.session_state.feedList.append(unidecode(text))
                st.success("Feedback Added!")
                time.sleep(3)
                st.experimental_rerun()



    with tab2:
        st.header("Results")

        #se a lista de feedbacks armazenados nao estiver vazia
        if st.session_state.feedList != []:
            if st.button("Check Results"):
                with st.spinner(text="Calculating..."):

                    # para cada termo na lista de feedback, ele ira comparar com as 2 listas da api, calcular as pontua-
                    # ções e armazenar o resultado no dicionario results
                    i = 0

                    for feed in st.session_state.feedList:
                        goodScore = getGoodMatch(feed, goodList)
                        badScore = getBadMatch(feed, badList)
                        finalScore = goodScore[0] - badScore[0]
                        st.session_state.results[i] = [feed, finalScore]
                        i = i + 1


                    # baseado no resultado do dicionario, ele ira utilizar a pontuação para classificar entre
                    # good, bad e neutral
                    results = getSimpleResult(st.session_state.results)

                    # separa as colunas do dicionario e converte em listas separadas para construir o df
                    data = listSplit(results)

                    # cria o df com base nos resultados
                    st.session_state.df = pd.DataFrame({"Feedback": st.session_state.feedList, "Score": data[0], "Result": data[1],"NPS":"NPS"})
                    # cria uma copia do df para excel para download
                    st.session_state.df.to_excel("results.xlsx")



                    st.session_state.positive = int(st.session_state.df[st.session_state.df["Score"] > 30].count()[0])
                    st.session_state.negative = int(st.session_state.df[st.session_state.df["Score"] < -30].count()[0])
                    st.session_state.neutral = int(st.session_state.df.count()[0]) - (st.session_state.positive + st.session_state.negative)

                    st.session_state.total = st.session_state.df.count()[0]

                    time.sleep(2)
                    st.success("Feedback Calculated!")


                    time.sleep(2)
                    st.experimental_rerun()

        # se a feedback list esta vazia é porque nao tem dado armazenado para mostrar
        else:
            st.warning("no data to share!")

        # true se o tamanho da df de resultado for maior que 0
        if len(st.session_state.df.index)>0:



            # mostra o resultado do bloco mensionado

            with st.expander("Manage table", expanded=True):
                st.title("test")
                # with open('results.xlsx', 'rb') as f:
                #     st.download_button('Download Table', f,
                #                        file_name='results.xlsx')
                #
                # if st.button("Delete input data"):
                #     with st.spinner(text="Deleting..."):
                #         time.sleep(2)
                #         st.experimental_memo.clear()
                #         for key in st.session_state.keys():
                #             del st.session_state[key]
                #         st.warning("Data deleted")
                #         time.sleep(2)
                #         st.experimental_rerun()

                #seaborn nps table

                sns.set_theme(style="darkgrid")

                # Initialize the matplotlib figure
                f, ax = plt.subplots(figsize=(6, 5))

                # Load the example car crash dataset
                crashes = sns.load_dataset("car_crashes").sort_values("total", ascending=False)

                # Plot the total crashes
                sns.barplot(x="NPS", y=st.session_state.df, data=st.session_state.df,
                            label="Positive", color="g")

                sns.barplot(x="NPS", y=st.session_state.df, data=st.session_state.df,
                            label="Neutral", color="y")

                sns.barplot(x="NPS", y=st.session_state.df, data=st.session_state.df,
                            label="Negative", color="r")

                # Add a legend and informative axis label
                ax.legend(ncol=2, loc="lower right", frameon=True)
                ax.set(xlim=(0, 24), ylabel="",
                       xlabel="Automobile collisions per billion miles")
                sns.despine(left=True, bottom=True)


                st.pyplot(f)
            col1, col2, col3 = st.columns([3,3,3])
            with col1:
                with st.expander("", expanded=True):
                    st.metric("", st.session_state.positive,
                              delta=(f"{st.session_state.positive / st.session_state.total * 100:.2f}%"),
                              help="Total of Positives occurrences. Percentage referring to the total of examples"
                              )

                    if st.button("Show",key='1'):
                        x = 1 #st.session_state.df = st.session_state.df["Result"=="good"]
            with col2:
                with st.expander("Neutral", expanded=True):
                    st.metric("", st.session_state.neutral,
                              delta=(f"{st.session_state.neutral / st.session_state.total * 100:.2f}%"),
                              delta_color="off",
                              help="Total of Neutral occurrences. Percentage referring to the total of examples"
                              )
                    if st.button("Show",key='2'):
                        x = 1 #st.session_state.df = st.session_state.df["Result"=="good"]
            with col3:
                with st.expander("Negatives", expanded=True):
                    st.metric("", st.session_state.negative,
                              delta=(f"{st.session_state.negative / st.session_state.total * 100:.2f}%"),
                              delta_color="inverse",
                              help="Total of Negatives occurrences. Percentage referring to the total of examples"
                              )
                    if st.button("Show",key='3'):
                        x = 1 #st.session_state.df = st.session_state.df["Result"=="good"]

        with st.expander("Result Table", expanded=True):
                keys = ["blaaaaaa","ble","bli","blo","blu","bl",]
                occ = []
                rel = []
                for i in range(len(keys)):
                    x = randrange(1,10)
                    y = random.uniform(0, 1.0)
                    occ.append(x)
                    rel.append(y)
                df = (
                            pd.DataFrame({"Keyword/Keyphrase":keys, "N_occurrences":occ , "Relevancy":rel})
                         .sort_values(by="Relevancy", ascending=False)
                         .reset_index(drop=True)
                    )
                #AgGrid(st.session_state.df)
                st.table(st.session_state.df)
                st.header("")

                df.index +=   1

                # Add styling
                cmGreen = sns.light_palette("green", as_cmap=True)
                cmRed = sns.light_palette("red", as_cmap=True)
                df = df.style.background_gradient(
                    cmap=cmGreen,
                    subset=[
                        "Relevancy",
                    ],
                )
                # df = df.set_table_styles([
                #     {"selector": "tr", "props": "line-height: 40px;"},
                #     {"selector": "td,th", "props": "line-height: inherit; padding: 0;"}
                # ])


                format_dictionary = {
                    "Relevancy": "{:.2%}",
                }

                df = df.format(format_dictionary)

                st.table(df)
    with tab3:
        st.text("tutorial")



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