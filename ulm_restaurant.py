# -*- coding: utf-8 -*-
"""ULM-restaurant.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1B_d8I0IOOXq2CT1CLsxIzvcHmEgJKXcp
"""

# pip install torch_nightly -f https://download.pytorch.org/whl/nightly/cu92/torch_nightly.html
# pip install fastai

# import libraries
import fastai
from fastai import *
from fastai.text import * 
import pandas as pd
import numpy as np
from functools import partial
import io
import os

df1 = pd.read_csv("merge_train.csv", header=None, names=['text', 'label'])
df2 = pd.read_csv("merge_test.csv", header=None, names=['text', 'label'])

df = pd.concat([df1, df2])
df.dropna(inplace = True)
df = df.sample(frac=1).reset_index(drop=True)

df['label'] = [int(e) for e in df['label']]

df = df[['label', 'text']]

"""PreProcessing"""

df['text'] = df['text'].str.replace("[^a-zA-Z]", " ")

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords 
stop_words = stopwords.words('english')

# tokenization 
tokenized_doc = df['text'].apply(lambda x: x.split())

# remove stop-words 
tokenized_doc = tokenized_doc.apply(lambda x: [item for item in x if item not in stop_words])

# de-tokenization 
detokenized_doc = [] 
for i in range(len(df)): 
    t = ' '.join(tokenized_doc[i]) 
    detokenized_doc.append(t) 

df['text'] = detokenized_doc

from sklearn.model_selection import train_test_split

# split data into training and validation set
df_trn, df_val = train_test_split(df, stratify = df['label'], test_size = 0.4, random_state = 12)

# Language model data
data_lm = TextLMDataBunch.from_df(train_df = df_trn, valid_df = df_val, path = "")

data_lm

# Classifier model data
data_clas = TextClasDataBunch.from_df(path = "", train_df = df_trn, valid_df = df_val, vocab=data_lm.train_ds.vocab, bs=32)

learn = language_model_learner(data_lm, arch = AWD_LSTM, pretrained=True, drop_mult=0.7)

# train the learner object with learning rate = 1e-2
learn.fit_one_cycle(1, 1e-2)

learn.save_encoder('ft_enc')

data_clas

learn = text_classifier_learner(data_clas, AWD_LSTM, drop_mult=0.7)
learn.load_encoder('ft_enc')

learn.fit_one_cycle(1, 1e-2)