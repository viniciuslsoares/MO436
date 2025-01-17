import copy
import lightning as L
import torch
import torchvision
from torch import nn

from torch.nn.functional import cosine_similarity
from torch import Tensor
from typing import List, Optional, Sequence, Tuple, Union
from lightly.utils.scheduler import cosine_schedule

# --- Utilities ---------------------------------------------------------

@torch.no_grad()
def update_momentum(model: nn.Module, model_ema: nn.Module, m: float):
    """Updates parameters of `model_ema` with Exponential Moving Average of `model`
    Momentum encoders are a crucial component fo models such as MoCo or BYOL.
    """
    for model_ema, model in zip(model_ema.parameters(), model.parameters()):
        model_ema.data = model_ema.data * m + model.data * (1.0 - m)

def deactivate_requires_grad(model: nn.Module):
    """Deactivates the requires_grad flag for all parameters of a model."""
    for param in model.parameters():
        param.requires_grad = False
        

# --- Loss ---------------------------------------------------------

class NegativeCosineSimilarity(torch.nn.Module):
    """Implementation of the Negative Cosine Simililarity used in the SimSiam[0] paper.
    [0] SimSiam, 2020, https://arxiv.org/abs/2011.10566"""

    def __init__(self, dim: int = 1, eps: float = 1e-8) -> None:
        """Same parameters as in torch.nn.CosineSimilarity

        Args:
            dim (int, optional):
                Dimension where cosine similarity is computed. Default: 1
            eps (float, optional):
                Small value to avoid division by zero. Default: 1e-8
        """
        super().__init__()
        self.dim = dim
        self.eps = eps

    def forward(self, x0: torch.Tensor, x1: torch.Tensor) -> torch.Tensor:
        return -cosine_similarity(x0, x1, self.dim, self.eps).mean()
    

# --- Model Parts ---------------------------------------------------------

class ProjectionHead(nn.Module):
    """Base class for all projection and prediction heads."""

    def __init__(
        self,
        blocks: Sequence[
            Union[
                Tuple[int, int, Optional[nn.Module], Optional[nn.Module]],
                Tuple[int, int, Optional[nn.Module], Optional[nn.Module], bool],
            ],
        ],
    ) -> None:
        super().__init__()

        layers: List[nn.Module] = []
        for block in blocks:
            input_dim, output_dim, batch_norm, non_linearity, *bias = block
            use_bias = bias[0] if bias else not bool(batch_norm)
            layers.append(nn.Linear(input_dim, output_dim, bias=use_bias))
            if batch_norm:
                layers.append(batch_norm)
            if non_linearity:
                layers.append(non_linearity)
        self.layers = nn.Sequential(*layers)
        
    def preprocess_step(self, x: Tensor) -> Tensor: return x

    def forward(self, x: Tensor) -> Tensor:
        x = self.preprocess_step(x)
        projection: Tensor = self.layers(x)
        return projection


class BYOLProjectionHead(ProjectionHead):
    """Projection head used for BYOL.
    "This MLP consists in a linear layer with output size 4096 followed by
    batch normalization, rectified linear units (ReLU), and a final
    linear layer with output dimension 256." [0]
    [0]: BYOL, 2020, https://arxiv.org/abs/2006.07733
    """

    def __init__(
        self, input_dim: int = 2048, hidden_dim: int = 4096, output_dim: int = 256
    ):
        super(BYOLProjectionHead, self).__init__(
            [
                (input_dim, hidden_dim, nn.BatchNorm1d(hidden_dim), nn.ReLU()),
                (hidden_dim, output_dim, None, None),
            ]
        )
        
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        
    def preprocess_step(self, x: Tensor) -> Tensor:
        return self.avgpool(x).flatten(start_dim=1)


class BYOLPredictionHead(ProjectionHead):
    """Prediction head used for BYOL.
    "This MLP consists in a linear layer with output size 4096 followed by
    batch normalization, rectified linear units (ReLU), and a final
    linear layer with output dimension 256." [0]
    [0]: BYOL, 2020, https://arxiv.org/abs/2006.07733
    """

    def __init__(
        self, input_dim: int = 256, hidden_dim: int = 4096, output_dim: int = 256
    ):
        super(BYOLPredictionHead, self).__init__(
            [
                (input_dim, hidden_dim, nn.BatchNorm1d(hidden_dim), nn.ReLU()),
                (hidden_dim, output_dim, None, None),
            ]
        )

# --- Class implementation ----------------------------------------------------------

class BYOLModel(L.LightningModule):
    def __init__(self, 
                    backbone=None,
                    learning_rate: float = 0.025,
                    ):
        # Learning rate do artigo: LR = 0,2 * BatchSize/256
        # Para um BatchSize de 32, LR = 0,2 * 32/256 = 0,025
        # Para um BAtchSize de 128, LR = 0,2 * 128/256 = 0,1
        super().__init__()
        if backbone:
            self.backbone = backbone
        else:
            resnet = torchvision.models.resnet18()
            self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        self.learning_rate = learning_rate
        self.projection_head = BYOLProjectionHead(2048, 4096, 256)
        self.prediction_head = BYOLPredictionHead(256, 4096, 256)

        self.backbone_momentum = copy.deepcopy(self.backbone)
        self.projection_head_momentum = copy.deepcopy(self.projection_head)

        deactivate_requires_grad(self.backbone_momentum)
        deactivate_requires_grad(self.projection_head_momentum)

        self.criterion = NegativeCosineSimilarity()

    def forward(self, x):
        y = self.backbone(x)
        z = self.projection_head(y)
        p = self.prediction_head(z)
        return p

    def forward_momentum(self, x):
        y = self.backbone_momentum(x)
        z = self.projection_head_momentum(y)
        z = z.detach()
        return z

    def training_step(self, batch, batch_idx):
        # print(len(batch[0]))
        momentum = cosine_schedule(self.current_epoch, 10500, 0.996, 1)
        # if self.current_epoch == 1: print(momentum)
        update_momentum(self.backbone, self.backbone_momentum, m=momentum)
        update_momentum(self.projection_head, self.projection_head_momentum, m=momentum)
        (x0, x1) = batch
        p0 = self.forward(x0)
        z0 = self.forward_momentum(x0)
        p1 = self.forward(x1)
        z1 = self.forward_momentum(x1)
        loss = 0.5 * (self.criterion(p0, z1) + self.criterion(p1, z0))
        self.log(
            f"train_loss",
            loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        
        return loss

    def configure_optimizers(self):
        return torch.optim.SGD(self.parameters(), lr=self.learning_rate)
        # return LARS(torch.optim.SGD(self.parameters(), lr=self.learning_rate), eps=1e-8)