import pandas as pd
import datetime
import csv

df = pd.read_csv('data/predictScore.csv')
predict_list = df.values.tolist()

output = []
for predict in predict_list:
    predict[0] = predict[0].replace('-','/')[2:]
    if(predict[1] > 0):
        predict[1] = 2
    elif(predict[1] < 0):
        predict[1] = 1
    else:
        predict[1] = 0
    output.append(predict)

dt_now = datetime.datetime.now().strftime('%Y%m%d')
file_name = 'formattedPredictCsv' + dt_now + '.csv'

with open(f"data/{file_name}",'w') as csv_file:
    fieldnames = ['日付','flag']
    writer = csv.writer(csv_file)
    writer.writerow(fieldnames)
    writer.writerows(output)

