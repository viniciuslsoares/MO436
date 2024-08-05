# MO346/MC934 Course work

This repository contains code and instructions to support the MO346/MC934 course work project. 

This project has the following structure:

- `data/`: contains the data used in the project. Your data should be stored here. This directory may contain large datasets and must not be added to the Git repository.
- `data_modules/`: contains implementations of `LightningDataModule` classes. These classes are responsible for loading and preprocessing data, and also for splitting the data into training, validation, and test sets.
- `models/`: contains implementations of `LightningModule` classes. These classes are responsible for defining the model architecture and implementing the `forward`, `training_step`, and `configure_optimizers`  methods.
- `transforms/`: contains implementations of Numpy/PyTorch transforms. These transforms are used to preprocess data before feeding it to the model.
- `best_results/`: contains the scripts to pretrain the backbone, train the downstream model, and evaluate the downstream model with the best hyperparameters (e.g., learning rate) for each technique. The scripts in this directory must follow the API defined by the professor.
- `report_results/`: contains the scripts to generate the results presented at the technical report. 

## Tutorial notebooks

The `ipynb` files at the root directory (e.g., `1-HAR-dataloader-exploration.ipynb`, `2-HAR-MLP-training.ipynb`, etc.) are tutorial notebooks with instructions on how to read the HAR/seismic dataset and train ML models to solve the HAR/seismic tasks.

## Installation

We use VSCode Containers to run the project. To run the project, you need to have Docker and VSCode installed on your machine.
If you don't know how to use Containers in VSCode, you can follow the instructions in the [following link](https://github.com/otavioon/container-workspace).

Once inside the container, you can install the dependencies, running the following command:

```bash
pip install -r requirements.txt
```

## Running the example code

To run the example code, you must change into the `best_results/har/` directory and run the following commands:

```bash
python BT_pretrain.py  
python BT_train.py
python BT_evaluate.py
```
Other variations of prefixes follows the name of the backbone and technique, for example TNC_GRU or TNC_Conv, always with the rest of the command following the structure of the given repository.

The pretrain script includes downloading the dataset from [drive](https://drive.google.com/drive/folders/1x4UGHgREdgMMXPlGiLvVIbbsnLToALXc) for HAR. The weights and checkpoints can be found at [this link](https://drive.google.com/drive/folders/1XUWH9cb-0Hex-uPQN6MKXhGW5V4TxtnR?usp=drive_link) and can be downloaded and put into the `best_results/HAR/` folder to replicate the experiments. Outputs will be produced at the `report_results/` folder. To run in a supervised or self supervised manner with less than 100% of data, scripts in this folder can be used following:

```bash
python supervised_train_downstream.py GRU 
python few_data_train_downstream.py TNC_GRU
```

## Authors

- [Otávio Napoli](https://github.com/otavioon)
- [Edson Borin](https://github.com/eborin)
- [Gabriel Gutierrez](https://github.com/gabrielbg0)

## License

This project is licensed under GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

