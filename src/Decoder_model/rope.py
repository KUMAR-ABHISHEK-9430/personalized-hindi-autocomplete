import torch
import torch.nn as nn


class RotaryPositionEmbedding(nn.Module):

    def __init__(
        self,
        d_model: int = 256,
        context_length: int = 128,
        base: int = 10000,
    ):
        super().__init__()

        assert d_model % 2 == 0, "Embedding dimension must be even."

        self.d_model = d_model
        self.context_length = context_length

        # (d_model/2,)
        inv_freq = 1.0 / (
            base ** (torch.arange(0, d_model, 2).float() / d_model)
        )

        # positions
        positions = torch.arange(context_length).float()

        # (context_length, d_model/2)
        angles = torch.outer(positions, inv_freq)

        self.register_buffer(
            "cos_cached",
            torch.cos(angles),
        )

        self.register_buffer(
            "sin_cached",
            torch.sin(angles),
        )

    def rotate_half(self, x):
        """
        x : (..., d_model)

        [x1 x2 x3 x4]
        ↓
        [-x2 x1 -x4 x3]
        """

        x_even = x[..., ::2]
        x_odd = x[..., 1::2]

        rotated = torch.stack(
            (-x_odd, x_even),
            dim=-1,
        )

        return rotated.flatten(start_dim=-2)

    def forward(self, q, k):

        seq_len = q.size(1)

        cos = self.cos_cached[:seq_len]
        sin = self.sin_cached[:seq_len]

        cos = cos.repeat_interleave(2, dim=-1)
        sin = sin.repeat_interleave(2, dim=-1)

        cos = cos.unsqueeze(0)
        sin = sin.unsqueeze(0)

        q = q * cos + self.rotate_half(q) * sin
        k = k * cos + self.rotate_half(k) * sin

        return q, k