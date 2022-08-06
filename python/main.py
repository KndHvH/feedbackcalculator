import streamlit as st
import json
import pandas as pd
from unidecode import unidecode
from api import *
from match import *
from simpleResult import *
from listSplit import *

#json api import
goodList = apiGood()
badList = apiBad()


# test.json file import (test only)
feedList=[]
df = "O creme é grosso mas simplesmente derrete na pele, não fica nada oleoso, deixa a pele super macia e hidratada sem ficar peguenta, não deixa resíduo e nem aquele “filme” que alguns hidratantes deixam. O cheiro é sensacional, bem docinho com um fundo cítrico maravilhoso. Simplesmente amei, já acabei a amostrinha de 25ml que recebi e já quero comprar o full size. Espero que a sephora traga as fragrâncias da marca!"
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

