import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
import spacy

nlp = spacy.load("es_core_news_sm")


def preprocess(txt):
    """
    This function returns a preprocessed list of texts 
    :param txt: list containing texts
    :return: preprocessed list of texts
    """
    sw = stopwords.words('spanish')
    space_pattern = '\s+'
    special_letters =  "[^a-zA-Z#]]"
    p_txt = []

    for resume_text in txt : 
            # Convert to lowercase
        resume_text = resume_text.lower()
        resume_text = re.sub(space_pattern, ' ', resume_text)# remove extra spaces
        # Remove special characters and punctuation
        resume_text = re.sub(r'[^\w\s]', '', resume_text)
        
        # Tokenization
        tokens = word_tokenize(resume_text, language='spanish')
        
        # Remove stopwords
        stop_words = set(stopwords.words('spanish'))
        tokens = [token for token in tokens if token not in stop_words]
        
        # Stemming
        stemmer = SnowballStemmer('spanish')
        stemmed_tokens = [stemmer.stem(token) for token in tokens]
        
        # Join the tokens back into a single string
        preprocessed_resume = ' '.join(stemmed_tokens)
        
        p_txt.append(preprocessed_resume)
        # print("-------------------")
        # print(preprocessed_resume)
        # text = re.sub(space_pattern, ' ', resume)# remove extra spaces
        # text = re.sub(special_letters, ' ', text)#remove special characteres
        # text = re.sub(r'[^\w\s]', '',text)#remove punctuations
        # #text = text.split() #split words in a text
        # text = [word for word in text if word.isalpha()] #keep alphabetic word
        # text = [w for w in text if w not in sw] #remove stop words
        # text = [item.lower() for item in text] #lowercase words
        # p_txt.append(" ".join(text))#joins all words
    return p_txt
