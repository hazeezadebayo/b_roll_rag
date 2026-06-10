"""
TLDR: Uses NLTK to strip stop words and extract core nouns/verbs from natural sentences.
"""
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Ensure required lightweight NLTK resources are downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)

class KeywordExtractor:
    @staticmethod
    def extract(sentence: str) -> str:
        """
        Takes a sentence like "A young person making coffee in the morning"
        and returns a URL-safe query string like "person+making+coffee+morning"
        """
        if not sentence:
            return ""
            
        # Tokenize words
        words = word_tokenize(sentence)
        
        # Part-of-speech tagging (identifies nouns, verbs, adjectives)
        tagged_words = pos_tag(words)
        
        # Filter for Nouns (NN), Verbs (VB), Adjectives (JJ)
        allowed_tags = {'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ'}
        stop_words = set(stopwords.words('english'))
        
        keywords = [
            word.lower() for word, tag in tagged_words 
            if tag in allowed_tags and word.lower() not in stop_words and word.isalnum()
        ]
        
        # Fallback to original string if extraction is too aggressive and yields nothing
        if not keywords:
            return sentence
            
        # Join with '+' for immediate Pexels API readiness
        return "+".join(keywords)

if __name__ == "__main__":
    test_query = "A young person making coffee in the morning"
    print("Cleaned Query:", KeywordExtractor.extract(test_query))
    # Output: person+making+coffee+morning