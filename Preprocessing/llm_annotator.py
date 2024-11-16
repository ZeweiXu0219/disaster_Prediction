import os
import sys
import yaml
import json
import requests
cur = os.getcwd()
sys.path.append(cur)
from tqdm import tqdm
from utils.utils import read_config, requests_parser, make_requests

class Annotator():
    def __init__(self, config_path, prompthub_path):
        self.config_path = config_path
        self.prompthub_path = prompthub_path
        self.system = ""
        self.prompt = ""
        self.model = ""
        self.url = ""
    def get_config(self):
        """
        get the config of annotator and annotator prompt

        default:
            url: "https://api.openai.com/v1/chat/completions"
            model: gpt-4o-mini
        
        Raises:
            ValueError: if there is no openai-api-key and prompt detected, the ValueError will be raised.
        """
        ## get basic config
        all_config = read_config(self.config_path)
        data = all_config['Annotator']
        openai_api_key = data.get("openai-api-key","")
        self.model = data.get("model", "gpt-4o-mini")
        self.url = data.get("url", "https://api.openai.com/v1/chat/completions")
        if not openai_api_key:
            raise ValueError("there is NO openai-api-key !!!")
        else:
            # self.openai_api_key = openai_api_key
            os.environ['OPENAI_API_KEY'] = openai_api_key
            
        ## get prompt config
        prompts = read_config(self.prompthub_path)
        self.system = prompts['annotation'].get("system","")
        self.prompt = prompts['annotation'].get("prompt","")
        if not self.prompt:
            raise ValueError("No Annotator Prompt !!!")
        
        # print(self.system)
        # print(self.prompt)
        # print(self.openai_api_key)
        # print(self.model)
    
    def __call__(self,querys):
        self.get_config()
        result = []
        for q in tqdm(querys):
            self.prompt = self.prompt.replace("{query}",str(q))
            response = make_requests(self.url, self.model, self.prompt)
            result.append(response)
        return result

if __name__ == "__main__":
    pwd = os.getcwd()
    config_path = os.path.join(pwd,"config/config.yaml")
    prompthub_path = os.path.join(pwd,"config/PromptHub.yaml")
    api_caller = Annotator(config_path=config_path, prompthub_path=prompthub_path)
    query = 'Fire in Berlin CT Lamentation Mountain #Connecticut #Wildfire'
    result = api_caller([query])
    print(requests_parser(result[0]))