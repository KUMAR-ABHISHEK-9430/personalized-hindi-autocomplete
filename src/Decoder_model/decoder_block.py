import torch
import torch.nn as nn

from .attention import CausalSelfAttention
from .feed_forward import FeedForward


class DecoderBlock(nn.Module):

    def __init__(
        self,
        d_model=256,
        context_length=128,
        dropout=0.1,
    ):
        super().__init__()

        self.ln1 = nn.LayerNorm(d_model)

        self.attention = CausalSelfAttention(
            d_model=d_model,
            context_length=context_length,
            dropout=dropout,
        )

        self.ln2 = nn.LayerNorm(d_model)

        self.ffn = FeedForward(
            d_model=d_model,
            expansion_factor=4,
            dropout=dropout,
        )

    def forward(self, x):

        # -------------------------
        # Attention Block
        # -------------------------

        x = x + self.attention(
            self.ln1(x)
        )

        # -------------------------
        # Feed Forward Block
        # -------------------------

        x = x + self.ffn(
            self.ln2(x)
        )

        return x