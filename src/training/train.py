import torch
import torch.nn as nn

from pathlib import Path

from Decoder_model.model import GPT
from training.trainer import Trainer
from Dataset.DataSet import train_loader, test_loader


device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(device)


# -------------------------
# Vocabulary size
# -------------------------

VOCAB_SIZE = 8000       #  sentencepiece vocab
CONTEXT = 128
EMBED_DIM = 256
NUM_BLOCKS = 4
DROPOUT = 0.1


model = GPT(
    vocab_size=VOCAB_SIZE,
    context_length=CONTEXT,
    d_model=EMBED_DIM,
    num_blocks=NUM_BLOCKS,
    dropout=DROPOUT,
)

model = model.to(device)

# Enable only after confirming one successful training run
# model = torch.compile(model)

print(
    "Parameters:",
    sum(
        p.numel()
        for p in model.parameters()
    )
)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=3e-4,
    betas=(0.9, 0.95),
    weight_decay=0.01,
    fused=(device.type == "cuda"),
)

criterion = nn.CrossEntropyLoss()

trainer = Trainer(
    model=model,
    train_loader=train_loader,
    test_loader=test_loader,
    optimizer=optimizer,
    criterion=criterion,
    device=device,
    checkpoint_dir="checkpoints",
    epochs=30,
)

trainer.fit(
    epochs=30,
)