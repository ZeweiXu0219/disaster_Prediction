import json
import pandas as pd
from utils.utils import code_parser
from sklearn.metrics import classification_report


llm_result_path = "data/test_data/disaster_prediction_no_sft_1B.json"
data_path = "data/test.csv"
result = json.load(open(llm_result_path,"r"))
result = result['result']
data = pd.read_csv(data_path)
data['label'] = data['label'].fillna(0).astype(int)

llm_result = []
for res in result:
    str_result = code_parser(res)
    str_result = str_result.replace("\n","")
    str_result = str_result.replace("nan","None")
    try:
        r = eval(str_result)
    except:
        r = {"result":"","location":"","disaster":""}
    llm_result.append(r)

df = pd.DataFrame(llm_result)
df['result'] = df['result'].astype(int)
classification_report(data['label'].tolist(),df['result'].tolist())
print("end")