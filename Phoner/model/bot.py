import nltk

nltk.download('punkt')
from nltk.stem.lancaster  import LancasterStemmer
import pickle
stemmer = LancasterStemmer()


import numpy as np
import tflearn
import tensorflow as tf
import json
import random

with open("Phoner/model/intents.json") as file:
    data = json.load(file)

try:
    
    with open("data.pickle", "rb") as f:
        words,labels, training, output = pickle.load(f)

except:
    words = []
    labels = []

    docs_x = []
    docs_y = []

    for intent in data ["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)  #stems the words in "patterns"
            words.extend(wrds) #adds all the stemmed wrds to the words list
            docs_x.append(wrds)
            docs_y.append(intent["tag"])
            
        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower() ) for w in words if w not in "?"]  #lowers all words
    words = sorted(list(set(words))) #removes all duplicate words

    labels = sorted(labels)

    #bag of words, one-hot-encoding - video 2 Tim, around 4 min

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds =[stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1) #adding a 1 if the words exists
            else:
                bag.append(0) #adding a 0 if the word doesnt exists

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1
    
        training.append(bag)
        output.append(output_row)

    training = np.array(training)
    output = np.array(output)
    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)


tf.compat.v1.reset_default_graph() #reset any data in the model

net = tflearn.input_data(shape=[None, len(training[0])])  #sets the standard lenght of the training data set to 0 is all data sets will be equally long

net= tflearn.fully_connected(net, 8 ) #creates the first layer with 8 nuerons in the hidden layer
net= tflearn.fully_connected(net, 8 )
net= tflearn.fully_connected(net, 8 )
net= tflearn.fully_connected(net, len(output[0]), activation="softmax" ) #sets the expected output dimensions and selects the activation function prøv evt sigmoid
net= tflearn.regression(net)

model = tflearn.DNN(net)
try:
    
    model.load("model.tflearn")
except:
    model = tflearn.DNN(net)
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")

#creates a bag of words based on the input, and matches it with our words list based on the data we input for training
def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))] #creates a list of the lenght of our possible words listnan initiates all values to 0 

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words): #checks if word from sentence if in words list and adds a 1 each time
            if w == se:
                bag[i] = 1
            
    return np.array(bag)


def chat(inp):    
    while True:
        results = model.predict([bag_of_words(inp, words)])  # gives a probability rating based on which "intent" fits most with our input bag of words #video 4 min 10 explain   
        results_index = np.argmax(results) #returns the position of the MAX number, in other words the intent with highest probability        
        tag = labels[results_index] #adds the label name based on psoition
        if results.tolist()[0][results_index] > 0.7:           
            for tg in data["intents"]: #gets a list of all possible responses for the assessed intent
                if tg['tag'] == tag:
                    responses = tg['responses']          
            return random.choice(responses), tag
        else:          
            return "I didn't get that please get back to me" ,"No Label"
    
    



        

