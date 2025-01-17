import glob
import os
import lightning as L
from lightning.pytorch.utilities.types import EVAL_DATALOADERS
import tifffile as tiff
from torch.utils.data import DataLoader, Dataset
from pathlib import Path


class ParihakaDataset(Dataset):
    """Unsupervised dataset for parihaka for BYOL pretext task.
    Parameters
    ----------
        data_dir: str
            The directory path where the data files are located.
        transform: callable, optional
            A function/transform that takes in a np.array representing the 
            sample feattures and returns a transformed version of this sample
            Default is None.
    """
    
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.files = glob.glob(os.path.join(root_dir, "*.tif"))

    def __len__(self):
        return int(len(self.files))

    def __getitem__(self, idx):

        img = tiff.imread(self.files[idx]).transpose(2, 0, 1)
        if self.transform:
            return self.transform(img)
        else: 
            return img
        
    
class ParihakaDataModule(L.LightningDataModule):
    def __init__(self, root_dir, batch_size=8, num_workers=None, transform=None):
        super().__init__()
        self.root_dir = root_dir
        self.batch_size = batch_size
        self.transform = transform
        self.num_workers = num_workers if num_workers else os.cpu_count()
        self.setup()

    def setup(self, stage=None):
        self.train_dataset = ParihakaDataset(Path(self.root_dir) / "train", transform=self.transform)
        self.val_dataset = ParihakaDataset(Path(self.root_dir) / "val", transform=self.transform)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True, drop_last=True, num_workers=self.num_workers)
    
    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size, shuffle=True, drop_last=True, num_workers=self.num_workers)
