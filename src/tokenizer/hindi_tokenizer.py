#  what in this?
#  this consiste script that uses unigram algo from sentencepiece to tokenize hindi text and generate a tokenizer model for hindi language.



import sentencepiece as spm







if __name__ == "__main__":
    DATA_FILE = r"C:\projects\auto_complete\personalized-hindi-autocomplete\src\data_extraction\cleaned_tokenizer_data.txt"


    spm.SentencePieceTrainer.train(
    input=DATA_FILE,
    model_prefix="personalized_hindi_autocomplete",
    vocab_size=8000,
    model_type="unigram",
    character_coverage=1.0,
    normalization_rule_name="identity",
    user_defined_symbols = ["<eod>"],

    
    # Don't invent huge "word" tokens
    max_sentencepiece_length=16,

    # Keep whitespace marker
    add_dummy_prefix=True,

    # Shuffle input before training
    shuffle_input_sentence=True,
)


    