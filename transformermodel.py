import pandas as pd
import numpy as np
import re
import string
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

#imports specific layers from the Keras library within TensorFlow are commonly used in neural network architectures for tasks like natural language processing.
from tensorflow.keras.layers import Input, Dense, GlobalAveragePooling1D, Embedding, MultiHeadAttention, Dropout

# Model class is used to create deep learning models by specifying the input and output layers
from tensorflow.keras.models import Model

#This line imports the Adam optimizer from the Keras library within TensorFlow.Adam is a popular optimization algorithm used for training deep learning models.
from tensorflow.keras.optimizers import Adam

# Early stopping is a technique used to prevent overfitting by stopping the training process when the performance on a validation dataset stops improving.
from tensorflow.keras.callbacks import EarlyStopping

#TextVectorization is used to convert raw text data into numerical tensors that can be fed into a neural network.
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

#imports the TensorFlow library itself, which provides a set of tools and functionalities for building and training deep learning models.
import tensorflow as tf

# Load the dataset
df = pd.read_csv("train.csv", encoding='ISO-8859-1')

# Preprocess text data
def preprocess_text(text):
    if isinstance(text, str):
        # removes punctuation from the text string using the translate() method along with str.maketrans() function
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.lower()
        text = re.sub(r'\s+', ' ', text).strip() #strip() method is then called to remove leading and trailing whitespace,sub()- substitute 1 or more whitespace with single space
        text = re.sub(r'[^\x00-\x7F]+', ' ', text) #uses a regular expression to remove non-ASCII characters from the text string. Characters outside the ASCII range (0-127) are replaced with a space
    elif isinstance(text, float):  
        text = str(text)  
    return text

df['text'] = df['text'].apply(preprocess_text)

# Tokenization and padding
tokenizer = Tokenizer()
tokenizer.fit_on_texts(df['text'])
max_length = 100  
sequences = tokenizer.texts_to_sequences(df['text'])
X = pad_sequences(sequences, maxlen=max_length, padding='post')

# Label Encoding
label_encoder = LabelEncoder()
df['label'] = label_encoder.fit_transform(df['sentiment'])
y = df['label']

# Train-test split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Model architecture
embedding_dim = 32  
num_heads = 2   #line sets the number of attention heads for the MultiHeadAttention layer. Multi-head attention allows the model to focus on different parts of the input data
ff_dim = 32   # line sets the dimensionality of the feedforward layer. The feedforward layer is a component of the Transformer architecture
vocab_size = len(tokenizer.word_index) + 1

#line defines the input layer of the model. The shape parameter specifies the shape of the input data
inputs = Input(shape=(max_length,)) 
embedding_layer = Embedding(vocab_size, embedding_dim)(inputs)
#It takes the embeddings from the previous layer as input and applies multi-head attention mechanism to capture dependencies between words in the sequence.
attention_output = MultiHeadAttention(num_heads=num_heads, key_dim=embedding_dim)(embedding_layer, embedding_layer)
attention_output = GlobalAveragePooling1D()(attention_output)
outputs = Dense(3, activation='softmax')(attention_output)#line adds a dense layer with softmax activation function to the output of the global average pooling laye


model = Model(inputs=inputs, outputs=outputs)
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Training the model
history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_val, y_val))

# Save the model
model.save("sentiment_model.h5")

# Save tokenizer word index
np.save("tokenizer_word_index.npy", tokenizer.word_index)

# Save label encoder's classes
np.save("label_encoder_classes.npy", label_encoder.classes_)

# Load the saved model
loaded_model = tf.keras.models.load_model("sentiment_model.h5")

# Define a function to plot confusion matrix
def plot_confusion_matrix(y_true, y_pred, classes):
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    df_cm = pd.DataFrame(cm_norm, index=classes, columns=classes)
    plt.figure(figsize=(10, 7))
    sns.heatmap(df_cm, annot=True, cmap='Blues', fmt=".2f")
    plt.xlabel('Predicted labels')
    plt.ylabel('True labels')
    plt.title('Confusion Matrix')
    plt.show()

# Preprocess input text and make prediction
input_text = "Bad website"
preprocessed_text = preprocess_text(input_text)

input_sequence = tokenizer.texts_to_sequences([preprocessed_text])
input_sequence_padded = pad_sequences(input_sequence, maxlen=max_length, padding='post')

#padded input sequence is passed to the loaded_model for prediction using the predict method
prediction = loaded_model.predict(input_sequence_padded)

# Convert prediction to class label,np.argmax is a NumPy function that returns the index of the maximum value along a specified axis of an array
predicted_label = np.argmax(prediction)

# Convert label back to original sentiment label
predicted_sentiment = label_encoder.inverse_transform([predicted_label])[0]

print("Predicted sentiment:", predicted_sentiment)


val_predictions = loaded_model.predict(X_val)
val_predicted_labels = np.argmax(val_predictions, axis=1)


plot_confusion_matrix(y_val, val_predicted_labels, label_encoder.classes_)
