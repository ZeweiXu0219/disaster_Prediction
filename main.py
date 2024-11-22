import os
import sys
import logging
import datetime
import argparse
import pandas as pd
from tqdm import tqdm
from utils.utils import read_config, save_file, make_requests, requests_parser

# 设置日志的基本配置

logger = logging.getLogger(__name__)

crawler_data_path = "data/crawler_dataset_labeled_gpt4o_1105.csv"

def setup_logging():
    """
    设置日志输出到文件和控制台
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = f"logs/disaster_prediction_{timestamp}.log"

    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(), 
            logging.FileHandler(log_file_path, mode='a', encoding='utf-8') 
        ]
    )
    logger.info("Logging initialized. Logs will be written to: %s", log_file_path)

def get_prompt(config_path):
    prompts = read_config(config_path)
    system = prompts['annotation'].get("system","")
    prompt = prompts['annotation'].get("prompt","")
    return system, prompt

def prepare(data_path, config_path):
    data = pd.read_csv(data_path)
    original_nums = len(data)
    # drop duplicates samples
    data = data.drop_duplicates()
    data.reset_index(drop=True, inplace=True)
    now_nums = len(data)
    if now_nums != original_nums:
        logging.info(f"{original_nums - now_nums} samples have been dropped!")
        logging.info(f"Now the dataset contain {now_nums} samples")
    else:
        logging.info("No sample drop!")

    res = []
    ## get prompt
    _, prompt = get_prompt(config_path)
    logging.info("start preparing the prompt pair!")
    for idx,row in tqdm(data.iterrows()):
        llamafactory_template = {"instruction":"",
                                 "input":"",
                                 "output":""}
        template = {"result":"","location":"","disaster":""}
        text = row['text']
        new_prompt = prompt.replace("{query}",str(text))
        template['result'] = row['label']
        template['location'] = row['location']
        template['disaster'] = row['disaster']

        result = "```json" + str(template) + "```"
        llamafactory_template['input'] = new_prompt
        llamafactory_template['output'] = result
        res.append(llamafactory_template)
    return res

def inference(url, data:list, model='llama3',template="openai"):
    if not isinstance(data, list):
        data = [data]
    ans = []
    raw_result = []
    logging.info("Start inference!")
    for prompt in tqdm(data):
        response = make_requests(url, model, prompt, template=template, need_api_key=False)
        result = requests_parser(response)
        ans.append(result)
        raw_result.append(response)
    return ans, raw_result

def main(state, data_path, config_path, save_path = None, port = 8000):
    """
    change different type of format of api by change different tails of state
    like 'infer_llamafactory' / 'infer_ollama'
    """
    setup_logging()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    if state == "prepare":
        prompt_pair = prepare(data_path=data_path, config_path=config_path)
        if save_path:
            save_file(prompt_pair, save_path=save_path, Type="json")
    elif state.startswith("infer"):
        data = pd.read_csv(data_path)
        
        _,prompt = get_prompt(config_path)
        prompts = [prompt.replace("{query}",str(query)) for query in data['text'].tolist()]
        if state.endswith("llamafactory"):
            url = f"http://localhost:{port}/v1/chat/completions"
            result,_ = inference(url, prompts)
        elif state.endswith("ollama"):
            url = "http://localhost:11434/api/generate"
            result,_ = inference(url, prompts, template="ollama")
        else:
            logging.error(f"your state is {state}, but we only have ['infer_llamafactory','infer_ollama']")
        if save_path:
            save_file({"result":result}, save_path=save_path, Type="json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Disaster Prediction Data Preparation Script")
    parser.add_argument("--state", type=str, required=True, default="prepare", help="which state you need to run.")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the input dataset CSV file.")
    parser.add_argument("--config_path", type=str, required=False, default="config/PromptHub.yaml", help="Path to the config file (YAML).")
    parser.add_argument("--save_path", type=str, required=False, help="Path to save the output JSON file.")
    parser.add_argument("--port", type=int, required=False, help="set the port of url")

    args = parser.parse_args()

    main(args.state, args.data_path, args.config_path, args.save_path, port=args.port)