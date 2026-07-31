import torch
import torch.nn as nn


class FeedForward(nn.Module):

    def __init__(
        self,
        d_model: int = 256,
        expansion_factor: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()

        hidden_dim = expansion_factor * d_model

        self.fc1 = nn.Linear(
            d_model,
            hidden_dim,
        )

        self.activation = nn.GELU()

        self.fc2 = nn.Linear(
            hidden_dim,
            d_model,
        )

        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        """
        x : (batch, seq_len, d_model)
        """

        x = self.fc1(x)

        x = self.activation(x)

        x = self.fc2(x)

        x = self.dropout(x)

        return x