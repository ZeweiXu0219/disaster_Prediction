import os
import sys
import pickle
import pandas as pd

from llm_annotator import Annotator
from preprocessing import Preprocessing
from utils.utils import requests_parser, code_parser

def main(texts):
    ## preprocessing
    cleaner = Preprocessing()
    cleaned_data = cleaner(texts)
    ## annotation
    pwd = os.getcwd()
    config_path = os.path.join(pwd,"config/config.yaml")
    prompthub_path = os.path.join(pwd,"config/PromptHub.yaml")

    annotator = Annotator(config_path,prompthub_path)
    responses = annotator(cleaned_data)
    
    ## save
    pickle.dump(responses, open("Preprocessing/data/crawler_data_result_gpt_4o.pkl","wb"))

def result_parser(raw_responses):
    result = []
    for response in raw_responses:
        if_parser = False
        for idx, method in enumerate(['split','regulation']):
            respo = requests_parser(response)
            respo = code_parser(respo,method=method)
            try:
                res = eval(respo)
                if_parser = True
                break
            except:
                print(f"尝试 {idx + 1} 失败")
            if idx == 2 and not if_parser:
                print(response)
                res = {"result":"","location":"","disaster":""}
        result.append(res)
    return result

if __name__ == '__main__':
    data = pd.read_csv("/Users/frankxu/Desktop/24Fall/ise540 final project/disaster_Prediction/crawler_dataset_labeled.csv") 
    main(data['text'].tolist())