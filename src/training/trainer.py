from pathlib import Path

import torch
from tqdm import tqdm
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter("runs/experiment_1")

class Trainer:

    def __init__(
        self,
        model,
        train_loader,
        test_loader,
        optimizer,
        criterion,
        device,
        checkpoint_dir,
        epochs,
    ):

        self.model = model
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device

        self.best_loss = float("inf")

        # Create checkpoint directory if it doesn't exist
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Mixed precision scaler.
        # Enabled only when training on CUDA.
        self.scaler = torch.amp.GradScaler(
            "cuda",
            enabled=(device.type == "cuda"),
        )

        # Cosine learning rate decay.
        # Learning rate starts at lr and gradually decreases to eta_min.
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer=self.optimizer,
            T_max=epochs,
            eta_min=1e-6,
        )

    def train_one_epoch(self):

        self.model.train()

        running_loss = 0.0

        progress_bar = tqdm(
            self.train_loader,
            desc="Training",
        )

        for x, y in progress_bar:

            # Faster CPU -> GPU copy because DataLoader uses pin_memory=True
            x = x.to(
                self.device,
                non_blocking=True,
            )

            y = y.to(
                self.device,
                non_blocking=True,
            )

            # Faster than filling gradients with zeros.
            self.optimizer.zero_grad(
                set_to_none=True,
            )

            # Automatic mixed precision.
            # Uses float16 where safe and float32 where necessary.
            with torch.amp.autocast(
                "cuda",
                enabled=(self.device.type == "cuda"),
            ):

                logits = self.model(x)

                batch_size, seq_len, vocab_size = logits.shape

                loss = self.criterion(
                    logits.reshape(
                        batch_size * seq_len,
                        vocab_size,
                    ),
                    y.reshape(
                        batch_size * seq_len,
                    ),
                )

            # Scale gradients to avoid underflow in fp16.
            self.scaler.scale(loss).backward()

            # Convert gradients back to fp32 before clipping.
            self.scaler.unscale_(self.optimizer)

            # Prevent exploding gradients.
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                max_norm=1.0,
            )

            # Optimizer step through GradScaler.
            self.scaler.step(self.optimizer)

            self.scaler.update()

            running_loss += loss.item()

            progress_bar.set_postfix(
                loss=f"{loss.item():.4f}",
            )

        return running_loss / len(self.train_loader)

    @torch.no_grad()
    def validate(self):

        self.model.eval()

        running_loss = 0.0

        for x, y in self.test_loader:

            x = x.to(
                self.device,
                non_blocking=True,
            )

            y = y.to(
                self.device,
                non_blocking=True,
            )

            with torch.amp.autocast(
                "cuda",
                enabled=(self.device.type == "cuda"),
            ):

                logits = self.model(x)

                batch_size, seq_len, vocab_size = logits.shape

                loss = self.criterion(
                    logits.reshape(
                        batch_size * seq_len,
                        vocab_size,
                    ),
                    y.reshape(
                        batch_size * seq_len,
                    ),
                )

            running_loss += loss.item()

        return running_loss / len(self.test_loader)

    def save_checkpoint(
        self,
        epoch,
        train_loss,
        val_loss,
        filename,
    ):

        checkpoint = {

            # Resume training from same epoch
            "epoch": epoch,

            # Model weights
            "model_state_dict": self.model.state_dict(),

            # AdamW state (momentum, variance etc.)
            "optimizer_state_dict": self.optimizer.state_dict(),

            # Scheduler state
            "scheduler_state_dict": self.scheduler.state_dict(),

            # GradScaler state for AMP
            "scaler_state_dict": self.scaler.state_dict(),

            # Best validation loss till now
            "best_loss": self.best_loss,

            # For logging
            "train_loss": train_loss,
            "val_loss": val_loss,

            # Exact random state for reproducibility
            "rng_state": torch.get_rng_state(),
        }

        if torch.cuda.is_available():
            checkpoint["cuda_rng_state"] = torch.cuda.get_rng_state()

        torch.save(
            checkpoint,
            self.checkpoint_dir / filename,
        )

    def load_checkpoint(
        self,
        path,
    ):

        checkpoint = torch.load(
            path,
            map_location=self.device,
        )

        self.model.load_state_dict(
            checkpoint["model_state_dict"],
        )

        self.optimizer.load_state_dict(
            checkpoint["optimizer_state_dict"],
        )

        self.scheduler.load_state_dict(
            checkpoint["scheduler_state_dict"],
        )

        self.scaler.load_state_dict(
            checkpoint["scaler_state_dict"],
        )

        self.best_loss = checkpoint["best_loss"]

        torch.set_rng_state(
            checkpoint["rng_state"],
        )

        if (
            torch.cuda.is_available()
            and "cuda_rng_state" in checkpoint
        ):
            torch.cuda.set_rng_state(
                checkpoint["cuda_rng_state"]
            )

        return checkpoint["epoch"]

    def fit(
        self,
        epochs,
    ):

        for epoch in range(epochs):

            train_loss = self.train_one_epoch()

            val_loss = self.validate()

            # Cosine scheduler updates once every epoch.
            self.scheduler.step()

            print(f"\nEpoch {epoch+1}/{epochs}")

            print(f"Train Loss : {train_loss:.4f}")

            print(f"Valid Loss : {val_loss:.4f}")

            print(
                f"Learning Rate : "
                f"{self.scheduler.get_last_lr()[0]:.2e}"
            )

            self.save_checkpoint(
                epoch,
                train_loss,
                val_loss,
                "latest.pt",
            )

            writer.add_scalar("Loss/Train", train_loss, epoch)
            writer.add_scalar("Loss/Validation", val_loss, epoch)
            writer.add_scalar(
                "LearningRate",
                self.scheduler.get_last_lr()[0],
                epoch,
            )

            if val_loss < self.best_loss:

                self.best_loss = val_loss

                self.save_checkpoint(
                    epoch,
                    train_loss,
                    val_loss,
                    "best.pt",
                )

                print("Best model saved.")