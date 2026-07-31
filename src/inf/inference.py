from pathlib import Path

import torch

from Decoder_model.model import GPT
from inf.predictor import Predictor


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

model = GPT(
    vocab_size=8000,
    d_model=196,
    
    num_blocks=2,
    context_length=128,
    # ffn_dim=768,
)

predictor = Predictor(
    model=model,
    tokenizer_path=Path(
        r"tokenizer/personalized_hindi_autocomplete.model"
    ),
    checkpoint_path=Path(
        "checkpoints/best.pt"
    ),
    device=device,
)

while True:

    prompt = input("\nPrompt : ")

    prediction = predictor.predict_next_token(
        prompt,
        # max_new_tokens=40,
        temperature=0.7,
        top_k=5,
    )

    print("\n")
    print(prediction)
    