import sys
sys.path.append('../../')

import torch
import lightning as L

import models.deeplabv3 as dlv3
from data_modules.seismic import F3SeismicDataModule
from models.upconv_classifier import SegmentationModel, PredictionHead

### - Extra Code --------------------------------------------------------------------
from torchmetrics import JaccardIndex
from torchmetrics import F1Score

def evaluate_model(model, dataset_dl):
    # Inicialize JaccardIndex metric
    jaccard = JaccardIndex(task="multiclass", num_classes=6)
    f1 = F1Score(num_classes=6, task="multiclass")
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # For each batch, compute the predictions and compare with the labels.
    for X, y in dataset_dl:
        # Move the model, data and metric to the GPU if available
        model.to(device)
        X = X.to(device)
        y = y.to(device)
        jaccard.to(device)
        f1.to(device)

        logits = model(X.float())
        predictions = torch.argmax(logits, dim=1, keepdim=True)
        jaccard(predictions, y)
        f1_score = f1(predictions, y)
    # Return a tuple with the number of correct predictions and the total number of predictions
    return (float(jaccard.compute().to("cpu"))), (float(f1_score.to("cpu")))

def report_IoU(model, dataset_dl, prefix=""):
    iou, f1 = evaluate_model(model, dataset_dl)
    print(prefix + " IoU = {:0.4f}".format(iou))
    print(prefix + " F1 = {:0.4f}".format(f1))

### ---------- DataModule -----------------------------------------------------------

# This function must instantiate and configure the datamodule for the downstream task.
# You must not change this function (Check with the professor if you need to change it).
def build_downstream_datamodule() -> L.LightningDataModule:
    return F3SeismicDataModule(root_dir="../../data/", batch_size=8, cap=1)

### ------------- Pretrained Model --------------------------------------------------

# This function must instantiate the downstream model and load its weights
# from checkpoint_filename.
# You might change this code, but must ensure it returns a Lightning model initialized with
# Weights saved by the *_train.py script.

def load_downstream_model(checkpoint_filename) -> L.LightningModule:
    
    head = PredictionHead(num_classes=6, in_channels=2048)
    
    backbone = dlv3.DeepLabV3Backbone()
    
    downstream_model = SegmentationModel.load_from_checkpoint(checkpoint_filename,
                                                                num_classes=6,
                                                                backbone=backbone,
                                                                head=head,
                                                                loss_fn=torch.nn.CrossEntropyLoss(),
                                                                learning_rate=0.007,
                                                                freeze_backbone=False,
                                                                )
    
    # downstream_model = dlv3.DeepLabV3Model.load_from_checkpoint(checkpoint_filename)
    return downstream_model

### --------------- Main -------------------------------------------------------------

# This function must not be changed. 
def main(SSL_technique_prefix): 
    
    # Load the pretrained model
    downstream_model = load_downstream_model(f'{SSL_technique_prefix}-best_downstream.ckpt')

    # Retrieve the train, validation and test sets.
    downstream_datamodule = build_downstream_datamodule()
    train_dl = downstream_datamodule.train_dataloader()
    val_dl   = downstream_datamodule.val_dataloader()
    test_dl  = downstream_datamodule.test_dataloader()    

    # Compute and report the mIoU metric for each subset
    report_IoU(downstream_model, train_dl, prefix="   Training dataset")
    report_IoU(downstream_model, val_dl,   prefix=" Validation dataset")
    report_IoU(downstream_model, test_dl,  prefix="       Test dataset")

if __name__ == "__main__":
    SSL_technique_prefix = "Byol"
    main(SSL_technique_prefix)
