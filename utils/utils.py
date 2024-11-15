import re
import os
import yaml
import json
import spacy
import pickle
import requests
from tqdm import tqdm

def save_file(content, save_path, Type = "pkl"):
    if Type == "pkl":
        if not save_path.endswith("pkl"):
            raise ValueError(f"save path format wrong, save type is {Type}, but you save {save_path}")
        pickle.dump(content, open(save_path, "wb"))
    elif Type == "json":
        if not save_path.endswith("json"):
            raise ValueError(f"save path format wrong, save type is {Type}, but you save {save_path}")
        json.dump(content, open(save_path, "wb"), ensure_ascii=False)


########### Requests ###########
def read_config(path):
    """
    read config yaml file

    Args:
        path (str): yaml file path

    Returns:
        dict: the content in yaml file
    """
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data

def make_requests(url, model, prompt, system='', need_api_key=True):
    """
    post a requests by using OpenAI API

    """
    template = {
        "model":model,
        "messages":[{"role":"user","content":prompt}]
    }
    
    if system:
        template["messages"].insert(0, {"role":"system","content":system})
    
    if need_api_key:
        try:
            openai_api_key = os.getenv('OPENAI_API_KEY')
        except:
            raise ValueError("Please first setup your OPENAI_API_KEY!! Cannot Find your OPENAI_API_KEY")
        
        headers = {"Content-Type":"application/json",
                "Authorization":f"Bearer {openai_api_key}"}
    else:
        headers = {"Content-Type":"application/json"}
    
    try:
        response = requests.post(url, headers=headers, json=template)
        result = response.json()
        return result
    except requests.exceptions.HTTPError as http_err:
        raise ValueError(f"HTTP 错误: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        raise ValueError(f"连接错误: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        raise ValueError(f"请求超时: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        raise ValueError(f"请求异常: {req_err}")   

def requests_parser(requests_json):
    """
    get the reply from response.

    Args:
        requests_json (dict): response body

    Raises:
        ValueError: if the input is not 'dict' type

    Returns:
        str: the real reply of the API
    """
    if not isinstance(requests_json,dict):
        raise ValueError(f"Input should be 'dict' not {type(requests_json)}")
    else:
        output = requests_json.get('choices',[])
        output = output[0]
        output = output.get('message',{})
        output = output.get('content','')
    return output

def code_parser(text, method='split', tag='json'):
    """
    the function is as a parser to extract the json format from the string output

    Args:
        text (str): output(response)
        method (str, optional): Now we have two method. 'split', 'regulation'. Defaults to 'split'
        tag (str, optional): what type of code that you make llm to generate. Defaults to 'json'.

    Returns:
        str: json format
    """
    if method == 'split':
        text = text.strip('```')
        text = text.replace("\n",'')
        text = text.strip()
        text = text.split(tag)[-1]
    elif method == 'regulation':
        json_pattern = re.compile(r'\{.*?\}', re.DOTALL)
        match = json_pattern.search(text)
        if match:
            text = match.group()
    return text

###############################
