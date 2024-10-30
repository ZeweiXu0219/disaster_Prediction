# disaster_Prediction
This is a Final Project of ISE540 in USC which is about the NLP(Natural Language Processing).

## Project Description
I get the topic from a [kaggle competiition](https://www.kaggle.com/c/nlp-getting-started) which is a simple binary classification.

Although it is just a final project of the class, I think it is a good opportunity to follow a real workflow used in the industrial field.

The workflow is as follow:

**Dataset** -> **Data Preprocessing** -> **Annotation(Labeling)** -> **EDA** -> **Model Selection** -> **Model Fine-tuning** -> **Evaluation** 

I will introduce what we have done in each part and break them down. Hope it will help you to understand our project and code.

## BreakDown Details

### 1. Datasets
Data Source: Twitter Texts

Approach: Web crawler ([code_source](https://www.bilibili.com/video/BV1mx4y1t7Uo/?spm_id_from=333.1007.top_right_bar_window_history.content.click&vd_source=e4945a960ebe99f5b861521b8f23add7))

Sample_count: 1430

#### Brief Explanation:

##### Web Crawler
In this part, we use **web crawler** to get some Twitter Texts. Because I am not familiar with the web crawler and what the operation of how to transfer the web data, I find the code on the *Bilibili* which is a Chinese video platform. Some details are expained in the video (HyperLink above)

### 2. Data Preprocessing

In the tweet texts, there are several elements that can be deleted.

#### 2.1. url

> "AWP Wildfire FN Giveaway! (227 Big Coins)
> Retweet
  Follow me & 
  @csgobig
>  
>    Follow http://kick.com/csgobig (optional)
>    
>    Winner will be picked in 7 days! "

#### 2.2. Non-English word

> like Chinese, Japanese and some other language.
>

#### 2.3. some punctuations
> like ... , \n , | , - 

### 3. Annotation

In this part, in order to increase our efficiency, we use *GPT-4o* to help us to do the labeling task.

### 4. EDA
### 5. Model Selection

Because this class is an NLP class, we want to try different kinds of models to solve the problem. Our logic is that we seperate the all NLP models into two categories. One is model for **<u>NLU (Natural Language Understanding)</u>** and another is model for **<u>NLG (Natural Language Generation)</u>**

#### 5.1. NLU

In this field, we think that the model related to the NLU tasks is like BERT and different optimized version of [BERT](https://arxiv.org/abs/1810.04805) such as [RoBERTa](https://arxiv.org/abs/1907.11692), [ALBERT](https://arxiv.org/abs/1909.11942), [DeBERTa](https://arxiv.org/abs/2006.03654) and etc.

In this case, we choose two famous models in the BERT family, the one is **RoBERTa** (I think it is the most famous optimized version of BERT) and another one is **DeBERTa** (the state-of-art model in NLU). 

#### 5.2. NLG

The hottest topic of AI field is LLM (Large Language Model). Therefore, the application of LLM should be considered when we talk about the NLG. 

There are many companies try to make their own LLM to have a better performance such as OpenAI, Antropic, Meta, Mistral AI, Alibaba, Baidu and etc. At the same time, many companies have made their own LLM open-sourced (except 'Open'AI), which helps many start-up companies or individual to develop their own LLM, application, software and etc..

For our project, we are going to use the [<u>**Llama3.1-8B-Instruct**</u>](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) and [<u>**Llama3.2-3B-Instruct**</u>](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct). These two models represent two main approaches for people to use LLM. The 8B model and 3B model represent Cloud and edge-device respectively.



### 6. Fine-tuning


### 7. Evaluation