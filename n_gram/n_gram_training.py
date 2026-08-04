import re
import pickle
import os
from collections import defaultdict, Counter
from n_gram.n_gram_data_preprocessing import preprocess_police_data

# We must define these as named functions (not lambdas) so the pickle module can save them!
def create_counter():
    return Counter()

def create_dict_of_counters():
    return defaultdict(create_counter)

def create_dict_of_dict_of_counters():
    return defaultdict(create_dict_of_counters)

class BackoffAutocomplete:
    def __init__(self):
        # We need separate dictionaries for each N-gram level
        self.quadgrams = defaultdict(create_dict_of_dict_of_counters) # N=4
        self.trigrams = defaultdict(create_dict_of_counters)          # N=3
        self.bigrams = defaultdict(create_counter)                    # N=2
        self.unigrams = Counter()                                     # N=1
        self.vocab = set()

    def train(self, preprocessed_sentences):
        """
        Trains the model by counting 4-grams, 3-grams, 2-grams, and 1-grams.
        """
        print("Training Backoff Model...")
        for sentence in preprocessed_sentences:
            tokens = sentence.split()
            self.vocab.update(tokens)
            
            # Count Unigrams
            for w in tokens:
                self.unigrams[w] += 1
                
            # Count Bigrams
            for i in range(len(tokens) - 1):
                w1, w2 = tokens[i], tokens[i+1]
                self.bigrams[w1][w2] += 1
                
            # Count Trigrams
            for i in range(len(tokens) - 2):
                w1, w2, w3 = tokens[i], tokens[i+1], tokens[i+2]
                self.trigrams[w1][w2][w3] += 1
                
            # Count Quadgrams (4-grams)
            for i in range(len(tokens) - 3):
                w1, w2, w3, w4 = tokens[i], tokens[i+1], tokens[i+2], tokens[i+3]
                self.quadgrams[w1][w2][w3][w4] += 1
                
        print(f"Training complete! Vocabulary size: {len(self.vocab)}")

    def predict_next_word(self, context_words, top_k=3):
        """
        Predicts the next word using Stupid Backoff.
        context_words: A list of the words the user just typed.
        """
        predictions = Counter()
        
        # We only need up to the last 3 words for a 4-gram model
        context = context_words[-3:] if len(context_words) >= 3 else context_words
        
        # 1. Try 4-Gram (Needs 3 words of context)
        if len(context) == 3:
            w1, w2, w3 = context
            if self.quadgrams[w1][w2][w3]:
                # If we find matches, return them immediately!
                return self._format_output(self.quadgrams[w1][w2][w3], top_k)
            # If nothing found, DROP the oldest word and BACKOFF
            context = context[1:]
            
        # 2. Try 3-Gram (Needs 2 words of context)
        if len(context) == 2:
            w1, w2 = context
            if self.trigrams[w1][w2]:
                return self._format_output(self.trigrams[w1][w2], top_k)
            # Drop oldest word and BACKOFF
            context = context[1:]
            
        # 3. Try 2-Gram (Needs 1 word of context)
        if len(context) == 1:
            w1 = context[0]
            if self.bigrams[w1]:
                return self._format_output(self.bigrams[w1], top_k)
                
        # 4. Try 1-Gram (Absolute fallback: return most common words overall)
        # We usually exclude structural tags like <s> from normal unigram suggestions
        safe_unigrams = {k: v for k, v in self.unigrams.items() if k not in ['<s>', '</s>', '<eod>']}
        return self._format_output(safe_unigrams, top_k)

    def save(self, filename="ngram_model.pkl"):
        """Saves the trained model to a binary file."""
        print(f"Saving model to {filename}...")
        with open(filename, 'wb') as f:
            pickle.dump(self.__dict__, f)
        print("Model saved successfully!")

    def load(self, filename="ngram_model.pkl"):
        """Loads a trained model from a binary file."""
        print(f"Loading model from {filename}...")
        with open(filename, 'rb') as f:
            self.__dict__.update(pickle.load(f))
        print("Model loaded successfully!")

    def _format_output(self, counter_dict, top_k):
        """Helper to format raw counts into sorted probabilities"""
        total = sum(counter_dict.values())
        sorted_items = sorted(counter_dict.items(), key=lambda x: x[1], reverse=True)
        return [(word, count / total) for word, count in sorted_items[:top_k]]

# --- Execution Example ---
if __name__ == "__main__":
    # Notice the 3 start tags for 4-gram compatibility
    # sample_data = [
    #     "<s> <s> <s> सेवा में , </s>",
    #     "<s> <s> <s> माननीय अपर मुख्य न्यायिक दण्डाधिकारी , प्रथम , महोदय </s>",
    #     "<s> <s> <s> मोहनियां ( कैमूर ) </s>",
    #     "<s> <s> <s> प्रसंग :- मोहनियां थाना कांड संख्या - <FIR_NUM> दिनांक - <DATE> धारा - 87 B.N.S </s>"
    # ]
    
    engine = BackoffAutocomplete()

    with open(r".\src\data_extraction\cleaned_tokenizer_data.txt", "r", encoding="utf-8") as f:
        raw_data = f.read()

    sample_data = preprocess_police_data(raw_data)

    # Check if a saved model exists to avoid retraining
    model_file = "ngram_model.pkl"
    if os.path.exists(model_file):
        engine.load(model_file)
    else:
        print("No pre-trained model found. Training a new model...")
        engine.train(sample_data)
        engine.save(model_file)
    
    print("\n--- Testing Stupid Backoff ---")
    
    # 4-Gram Hit
    print("\nUser typed: 'माननीय अपर मुख्य'")
    print(engine.predict_next_word(["माननीय", "अपर", "मुख्य"])) # Will predict 'न्यायिक'
    
    # 3-Gram Hit (Backoff triggered because user made a typo/skipped a word)
    print("\nUser typed: 'अपर मुख्य' (Skipped माननीय)")
    print(engine.predict_next_word(["अपर", "मुख्य"])) # Will still predict 'न्यायिक'!
    
    # 2-Gram Hit
    print("\nUser typed: 'थाना'")
    print(engine.predict_next_word(["थाना"])) # Will predict 'कांड'