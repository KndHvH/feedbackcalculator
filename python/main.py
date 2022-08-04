import streamlit as st
# import re
# from pyngrok import ngrok
from api import *
from match import *


goodList = apiGood()
badList = apiBad()

fb = "essa placa de vídeo é incrível, o desempenho dela para os jogos q testei são absurdo"

goodScore = getGoodMatch(fb,goodList)
badScore = getBadMatch(fb,badList)
finalScore = goodScore[0] - badScore[0]

print(goodScore)
print(badScore)
print(finalScore)