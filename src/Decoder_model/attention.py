import math

import torch
import torch.nn as nn
import torch.nn.functional as F
from .rope import RotaryPositionEmbedding

class CausalSelfAttention(nn.Module):

    def __init__(
        self,
        d_model: int = 256,
        context_length: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.d_model = d_model
        self.context_length = context_length

        # Q, K, V projections
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)

        # output projection
        self.out_proj = nn.Linear(d_model, d_model, bias=False)

        self.dropout = nn.Dropout(dropout)

        # causal mask
        mask = torch.triu(
            torch.ones(context_length, context_length),
            diagonal=1,
        )

        self.register_buffer(
            "causal_mask",
            mask.bool(),
        )

        self.rope = RotaryPositionEmbedding(
           d_model=d_model,
            context_length=context_length,
        )

    def apply_rope(self, q, k):
        
        return self.rope(q, k)

    def forward(self, x):

        # x -> (batch, seq_len, d_model)
        assert x.dim() == 3
        assert x.size(-1) == self.d_model         

        batch_size, seq_len, _ = x.shape

        q = self.q_proj(x)
        k = self.k_proj(x)
        v = self.v_proj(x)

        q, k = self.apply_rope(q, k)

        scores = torch.matmul(
            q,
            k.transpose(-2, -1),
        )

        scores = scores / math.sqrt(self.d_model)

        scores = scores.masked_fill(
            self.causal_mask[:seq_len, :seq_len],
            float("-inf"),
        )

        attention = F.softmax(scores, dim=-1)

        attention = self.dropout(attention)

        output = torch.matmul(
            attention,
            v,
        )

        output = self.out_proj(output)

        return output