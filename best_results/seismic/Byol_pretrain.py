import sys
sys.path.append('../..')

from torch import nn
import torch
import lightning as L
import pytorch_lightning as pl

import models.deeplabv3 as dlv3
import models.byol as byol_module
from transforms.byol import BYOLTransform
from data_modules.Parihaka_dataset import ParihakaDataModule as ByolDataModule
from pytorch_lightning.loggers import CSVLogger

# This function must save the weights of the pretrained model
def pretext_save_backbone_weights(pretext_model, checkpoint_filename):
    print(f"Saving backbone pretrained weights at {checkpoint_filename}")
    torch.save(pretext_model.backbone.state_dict(), checkpoint_filename)


### ---------- DataModule -----------------------------------------------------------

# This function must instantiate and configure the datamodule for the pretext task
# with the best parameters found for the seismic/HAR task.
# You might change this code, but must ensure it returns a Lightning DataModule.

def build_pretext_datamodule() -> L.LightningDataModule:
    # Build the transform object
    transform = BYOLTransform(input_size=256,
                            min_scale=0,
                            degrees=5,
                            r_prob=0.0,
                            h_prob=0.0,
                            v_prob=0.0,
                            collor_jitter_prob=0,
                            grayscale_prob=0,
                            gaussian_blur_prob=0,
                            solarize_prob=0.0
                            )
    # Create the datamodule
    return ByolDataModule(root_dir="../../data/seam_ai/images/",
                                batch_size=64,
                                transform=transform)

### --------------- LightningModule --------------------------------------------------

# This function must instantiate and configure the pretext model
# with the best parameters found for the seismic/HAR task.
# You might change this code, but must ensure it returns a Lightning model.

def build_pretext_model() -> L.LightningModule:
    # Build the backbone
    backbone = dlv3.DeepLabV3Backbone()
    # Loss function and projection head already inside LightningModule
    # Build the pretext model
    return byol_module.BYOLModel(backbone=backbone,
                                learning_rate=0.1)
    
### --------------- Trainer -------------------------------------------------------------

# This function must instantiate and configure the lightning trainer
# with the best parameters found for the seismic/HAR task.
# You might change this code, but must ensure you return a Lightning trainer.

def build_lightning_trainer() -> L.Trainer:
    return L.Trainer(
        accelerator="gpu",
        # max_epochs=1000,
        max_steps=10500,
        enable_checkpointing=False, 
        logger=CSVLogger("logs", name="Byol", version="best_bakcbone"),
        )
    
### --------------- Main -----------------------------------------------------------------

# This function must not be changed. 
def main(SSL_technique_prefix):

    # Build the pretext model, the pretext datamodule, and the trainer
    pretext_model = build_pretext_model()
    pretext_datamodule = build_pretext_datamodule()
    lightning_trainer = build_lightning_trainer()

    # Fit the pretext model using the pretext_datamodule
    lightning_trainer.fit(pretext_model, pretext_datamodule)

    # Save the backbone weights
    output_filename = f"./{SSL_technique_prefix}_best_bakcbone.pth"
    pretext_save_backbone_weights(pretext_model, output_filename)

if __name__ == "__main__":
    SSL_technique_prefix = "Byol"
    main(SSL_technique_prefix)
