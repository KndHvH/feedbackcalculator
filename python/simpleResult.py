def getSimpleResult(dict):
    for i in dict:
        if dict[i][1] > 30:
            dict[i] = [dict[i][0],dict[i][1],'good']

        elif dict[i][1] < -30:
            dict[i] = [dict[i][0],dict[i][1],'bad']

        else:
            dict[i] = [dict[i][0],dict[i][1],'neutral']
    return dict


