import torch
import sentencepiece as spm
from pathlib import Path

TOKENIZER_MODEL_PATH  = Path(r"C:\projects\auto_complete\personalized-hindi-autocomplete\src\tokenizer\personalized_hindi_autocomplete.model")



sp = spm.SentencePieceProcessor()

sp.load(TOKENIZER_MODEL_PATH.as_posix())


with open(r"C:\projects\auto_complete\personalized-hindi-autocomplete\src\data_extraction\cleaned_tokenizer_data.txt",encoding='utf-8') as f:
    data = f.read()


token_ids = sp.encode(data,out_type=int)
# print(token_ids)

torch.save(token_ids,"token_ids.pt")