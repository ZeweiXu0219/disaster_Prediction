import re
import os
import yaml
import spacy
import requests
from tqdm import tqdm

########### Annotation ###########
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

def make_requests(url, model, prompt, query, system='', need_api_key=True):
    """
    post a requests by using OpenAI API

    """
    prompt = prompt.replace("{query}",query)
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

###############################

########### Data Preprocessing ###########
def clean_url(text):
    """
    clean the url in text

    Args:
        text (str): tweet text

    Returns:
        str: cleaned text
    """
    url_pattern = r'(https?://[^\s]+)'
    urls = re.findall(url_pattern, text)
    
    for element in urls:
        text = text.replace(element, '')
    return text

def get_special_token(texts:list) -> list:
    
    if not isinstance(texts, list):
        raise ValueError(f"Type of Input 'texts' should be 'str', but we get {type(texts)}")
    
    nlp = spacy.load('en_core_web_sm')
    
    special_tokens = []
    for sentence in tqdm(texts):
        for tk in nlp(str(sentence)):
            if (tk.is_alpha and tk.lang_ == 'en') or tk.text.isdigit() or tk.is_punct or tk.is_space:
                continue
            else:
                if tk.text not in special_tokens and not tk.text.startswith('@') and '’' not in tk.text:
                    special_tokens.append(tk.text)
    
    return special_tokens

def is_float(value):
    if value.count('.') == 1:
        left, right = value.split('.')
        if (left.isdigit() or (left and left[0] == '-' and left[1:].isdigit())) and right.isdigit():
            return True
    elif value.isdigit() or (value and value[0] == '-' and value[1:].isdigit()):
        return True
    return False