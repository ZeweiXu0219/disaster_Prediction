import os
import sys
import pickle
import pandas as pd
from llm_annotator import Annotator
from preprocessing import Preprocessing

def main(texts):
    ## preprocessing
    cleaner = Preprocessing()
    cleaned_data = cleaner(texts)
    ## annotation
    pwd = os.getcwd()
    config_path = os.path.join(pwd,"config\config.yaml")
    prompthub_path = os.path.join(pwd,"config\PromptHub.yaml")

    annotator = Annotator(config_path,prompthub_path)
    responses = annotator(cleaned_data)
    
    ## save
    pickle.dump(responses, open("Preprocessing\data\llm_label_raw_result.pkl","wb"))


if __name__ == '__main__':
    data = pd.read_csv("..\crawler_dataset.csv") 
    main(data['text'].tolist())