import sys
sys.path.append('../../')

import torch
import lightning as L

import models.deeplabv3 as dlv3
from models.upconv_classifier import SegmentationModel, PredictionHead
from data_modules.seismic import F3SeismicDataModule
from pytorch_lightning.loggers import CSVLogger


### ---------- PreTrain  ------------------------------------------------------------

# This function should load the backbone weights
def load_pretrained_backbone(pretrained_backbone_checkpoint_filename):

    backbone = dlv3.DeepLabV3Backbone()
    backbone.load_state_dict(torch.load(pretrained_backbone_checkpoint_filename))
    return backbone

### ---------- DataModule -----------------------------------------------------------

# This function must instantiate and configure the datamodule for the downstream task.
# You must not change this function (Check with the professor if you need to change it).

def build_downstream_datamodule() -> L.LightningDataModule:
    return F3SeismicDataModule(root_dir="../../data/", batch_size=8, cap=1)


### --------------- LightningModule --------------------------------------------------

# This function must instantiate and configure the downstream model
# with the best parameters found for the seismic/HAR task.
# You might change this code, but must ensure it returns a Lightning model.

def build_downstream_model(backbone) -> L.LightningModule:
    
    pred_head = PredictionHead(num_classes=6, in_channels=2048)
    
    return SegmentationModel(num_classes=6,
                            backbone=backbone,
                            head=pred_head,
                            loss_fn=torch.nn.CrossEntropyLoss(),
                            learning_rate=0.007,
                            freeze_backbone=False)

### --------------- Trainer -------------------------------------------------------------

# This function must instantiate and configure the lightning trainer
# with the best parameters found for the seismic/HAR task.
# You might change this code, but must ensure you return a Lightning trainer.

def build_lightning_trainer(SSL_technique_prefix) -> L.Trainer:
    from lightning.pytorch.callbacks import ModelCheckpoint
    # Configure the ModelCheckpoint object to save the best model 
    # according to validation loss
    checkpoint_callback = ModelCheckpoint(
        monitor='val_loss',
        dirpath=f'./',
        filename=f'{SSL_technique_prefix}-best_downstream',
        save_top_k=1,
        mode='min',
    )
    return L.Trainer(
        accelerator="gpu",
        max_epochs=50,
        logger=CSVLogger("logs", name="Supervised", version="best_downstream"),
        callbacks=[checkpoint_callback])
    
### --------------- Main -----------------------------------------------------------------

# This function must not be changed. 
def main(SSL_technique_prefix):

    # Load the pretrained backbone
    pretrained_backbone_checkpoint_filename = f"./{SSL_technique_prefix}_best_bakcbone.pth"
    backbone = load_pretrained_backbone(pretrained_backbone_checkpoint_filename)

    # Build the downstream model, the downstream datamodule, and the trainer
    downstream_model = build_downstream_model(backbone)
    downstream_datamodule = build_downstream_datamodule()
    lightning_trainer = build_lightning_trainer(SSL_technique_prefix)

    # Fit the pretext model using the pretext_datamodule
    lightning_trainer.fit(downstream_model, downstream_datamodule)

if __name__ == "__main__":
    SSL_technique_prefix = "Byol"
    main(SSL_technique_prefix)
