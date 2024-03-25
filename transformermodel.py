import pandas as pd
import numpy as np
import re
import string
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


df = pd.read_csv("train.csv", encoding='ISO-8859-1')


def preprocess_text(text):
    if isinstance(text, str):
        
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        text = text.lower()
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    elif isinstance(text, float):  
        text = str(text)  
    return text

df['text'] = df['text'].apply(preprocess_text)


tokenizer = Tokenizer()
tokenizer.fit_on_texts(df['text'])


max_length = 100  
sequences = tokenizer.texts_to_sequences(df['text'])
X = pad_sequences(sequences, maxlen=max_length, padding='post')


label_encoder = LabelEncoder()
df['label'] = label_encoder.fit_transform(df['sentiment'])
y = df['label']


X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
print(X_train)

