# what this script contains



import torch
import torch.nn as nn

from .decoder_block import DecoderBlock


class GPT(nn.Module):

    def __init__(
        self,
        vocab_size: int = 8000,
        d_model: int = 256,
        context_length: int = 128,
        num_blocks: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.token_embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=d_model,
        )

        self.embedding_dropout = nn.Dropout(dropout)

        self.decoder_blocks = nn.ModuleList(
            [
                DecoderBlock(
                    d_model=d_model,
                    context_length=context_length,
                    dropout=dropout,
                )
                for _ in range(num_blocks)
            ]
        )

        self.final_layer_norm = nn.LayerNorm(d_model)

        self.lm_head = nn.Linear(
            d_model,
            vocab_size,
            bias=False,
        )

        # GPT-2 style weight tying
        self.lm_head.weight = self.token_embedding.weight

    def forward(self, input_ids):

        """
        input_ids : (batch, seq_len)
        """

        x = self.token_embedding(input_ids)

        x = self.embedding_dropout(x)

        for block in self.decoder_blocks:
            x = block(x)

        x = self.final_layer_norm(x)

        logits = self.lm_head(x)

        return logits