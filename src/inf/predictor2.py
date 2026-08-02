from pathlib import Path

import torch
import torch.nn.functional as F
import sentencepiece as spm


class Predictor:

    def __init__(
        self,
        model,
        tokenizer_path,
        checkpoint_path,
        device,
        context_window=128,
    ):

        self.device = device
        self.context_window = context_window

        self.model = model.to(device)

        checkpoint = torch.load(
            checkpoint_path,
            map_location=device,
            weights_only=False,
        )

        self.model.load_state_dict(
            checkpoint["model_state_dict"],
        )

        self.model.eval()

        self.sp = spm.SentencePieceProcessor()
        self.sp.load(str(tokenizer_path))




    @torch.no_grad()
    def predict(
        self,
        prompt,
        top_k=5,
    ):

        token_ids = self.sp.encode(
            prompt,
            out_type=int,
        )

        token_ids = token_ids[-self.context_window:]

        x = torch.tensor(
            token_ids,
            dtype=torch.long,
            device=self.device,
        ).unsqueeze(0)

        logits = self.model(x)

        logits = logits[:, -1, :]

        probs = F.softmax(
            logits,
            dim=-1,
        )

        values, indices = torch.topk(
            probs,
            top_k,
        )

        predictions = []

        for idx in indices[0]:
            predictions.append(
                self.sp.decode([idx.item()])
            )

        return predictions