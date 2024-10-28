import os
import re
import sys
import json
import spacy
import pandas as pd
from tqdm import tqdm


class Preprocessing():
    def __init__(self):
        self.special_tokens = []
    
    def clean_url(self,texts):
        """
        clean the url in text

        Args:
            text (list): tweet texts

        Returns:
            str: cleaned texts
        """
        result = []
        for sentence in texts:
            sentence = str(sentence)
            url_pattern = r'(https?://[^\s]+)'
            sentence = re.sub(url_pattern, '', sentence)
            result.append(sentence.strip())
        return result

    def get_special_tag(self, texts, tag):
        """
        get special tag of tweet texts like '@name' '#title'

        Args:
            texts (str): tweets
            tag (str): tag
        """
        all_tags = []
        for sentence in texts:
            tk_list = str(sentence).split()
            for tk in tk_list:
                if tk.startswith(tag) and tk not in all_tags:
                    all_tags.append(tk)
        return all_tags

    def get_special_token(self, texts:list) -> list:
        """
        find all the special tokens appeared in the whole texts

        Args:
            texts (list): datasets

        Raises:
            ValueError: Input validation

        Returns:
            list: all the appeared special tokens
        """
        if not isinstance(texts, list):
            raise ValueError(f"Type of Input 'texts' should be 'str', but we get {type(texts)}")
        
        nlp = spacy.load('en_core_web_sm')
        
        special_tokens = []
        for sentence in tqdm(texts):
            for tk in nlp(str(sentence)):
                if (tk.is_alpha and tk.lang_ == 'en') or self.is_valid_num(tk.text) or tk.is_punct or tk.is_space:
                    continue
                else:
                    if tk.text not in special_tokens and not tk.text.startswith('@') and '’' not in tk.text:
                        special_tokens.append(tk.text)
        return special_tokens

    def clean_texts(self, texts):
        result = []
        for sentence in texts:
            clean = re.sub(r'[^a-zA-Z0-9\s.,!?;:\'"()\-\#\@]', '', sentence)
            result.append(clean)
        return result
    
    def is_valid_num(self, value):
        if value.count('.') == 1:
            left, right = value.split('.')
            if (left.isdigit() or (left and left[0] == '-' and left[1:].isdigit())) and right.isdigit():
                return True
        elif value.isdigit() or (value and value[0] == '-' and value[1:].isdigit()) or (value and value[0] == '+' and value[1:].isdigit()):
            return True
        elif value.count(',') == 1:
            left, right = value.split(',')
            if (left.isdigit() or (left and left[0] == '-' and left[1:].isdigit())) and right.isdigit():
                return True
        return False

    def __call__(self,texts):
        cleaned_url_data = self.clean_url(texts)
        cleaned_sentences = self.clean_texts(cleaned_url_data)
        return cleaned_sentences
        

if __name__ == '__main__':
    data = pd.read_csv("..\crawler_dataset.csv") 
    cleaner = Preprocessing()
    cleaner(data['text'].tolist())