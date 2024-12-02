from .model import GPT
from .dataset import NameDataset
from .trainer import Trainer, TrainerConfig

import logging  # Ensure logging is imported
import torch.nn as nn
import torch
import random
random.seed(0)
logging.basicConfig(level=logging.INFO)


def initialize_vanilla_model(mconf):
    attention_model = None
    ### TODO:
    ### [part c]: Make some model here

    ### START CODE HERE
    attention_model = GPT(mconf)
    ### END CODE HERE
    return attention_model


def initialize_perceiver_model(mconf, bottleneck_dim=32):
    attention_model = None
    ### TODO
    ### [part g]: Make some other model here
    ### START CODE HERE
    logging.info("Initializing Perceiver Model with config: %s and bottleneck_dim: %d", mconf, bottleneck_dim)
    try:
        class PerceiverModel(GPT):
            def __init__(self, config):
                super().__init__(config)
                self.blocks = nn.ModuleList()
                self.blocks.append(DownProjectBlock(config))
                self.blocks.extend([Block(config) for _ in range(config.n_layer - 2)])
                self.blocks.append(UpProjectBlock(config))
            
            def forward(self, x):
                for block in self.blocks:
                    x = block(x)
                return x

        attention_model = PerceiverModel(mconf)
        logging.info("Perceiver Model initialized successfully")
    except Exception as e:
        logging.error("Error initializing Perceiver Model: %s", e)
    ### END CODE HERE

def finetune(reading_params_path, finetune_corpus_path, pretrain_dataset, block_size, model, finetune_lr=6e-4, writer=None):
    ### TODO:
    ### [part c] [part f]:
    ### - Given:
    ###     1. A finetuning corpus specified in finetune_corpus_path
    ###     2. A path reading_params_path containing pretrained model
    ###         parameters, or None if finetuning without a pretrained model
    ### - Goals:
    ###     1. If reading_params_path is specified, load these parameters
    ###         into the model
    ###     2. Finetune the model on this corpus
    ###
    ### - Make sure to use the following hyperparameters:
    ###     Hyperparameters for finetuning WITHOUT a pretrained model:
    ###         max_epochs=75
    ###         batch_size=256
    ###         learning_rate=6e-4
    ###         lr_decay=True
    ###         warmup_tokens=512*20
    ###         final_tokens=200*len(pretrain_dataset)*block_size
    ###         num_workers=0
    ###     Hyperparameters for finetuning WITH a pretrained model:
    ###         max_epochs=10
    ###         batch_size=256
    ###         learning_rate=6e-4
    ###         lr_decay=True
    ###         warmup_tokens=512*20
    ###         final_tokens=200*len(pretrain_dataset)*block_size
    ###         num_workers=0
    ###
    ###
    ### Note: Please use torch.load(reading_params_path, map_location=torch.device('cpu')) to load pretrained model 

    trainer_obj = None #Trainer object (see trainer.py for more details)
    tconf = None #TrainerConfig object (see trainer.py for more details)
    
    if reading_params_path is not None:
        model.load_state_dict(torch.load(reading_params_path, map_location=torch.device('cpu')))
    
    finetune_dataset = NameDataset(open(finetune_corpus_path, encoding='utf-8').read(), pretrain_dataset)

    tconf = TrainerConfig(
        max_epochs=75 if reading_params_path is None else 10,
        batch_size=256,
        learning_rate=finetune_lr,
        lr_decay=True,
        warmup_tokens=512 * 20,
        final_tokens=200 * len(pretrain_dataset) * block_size,
        num_workers=0
    )
    
    trainer_obj = Trainer(model, finetune_dataset, None, tconf)
    ### END CODE HERE ###


    return tconf, trainer_obj


def pretrain(pretrain_dataset, block_size, model, pretrain_lr=6e-3, writer=None):
    ### TODO:
    ### [part f]:
    ### - Given:
    ###     1. A corpus specified in pretrain_dataset
    ### - Goals:
    ###     1. Pretrain the model on this corpus
    ###
    ### - Make sure to use the following hyperparameters for pretraining:
    ###     max_epochs=650
    ###     batch_size=128
    ###     learning_rate=6e-3
    ###     lr_decay=True
    ###     warmup_tokens=512*20
    ###     final_tokens=200*len(pretrain_dataset)*block_size
    ###     num_workers=0

    tconf = None  # TrainerConfig object (see trainer.py for more details)
    trainer_obj = None  # Trainer object




   ### START CODE HERE
    tconf = TrainerConfig(
        max_epochs=650,
        batch_size=128,
        learning_rate=pretrain_lr,
        lr_decay=True,
        warmup_tokens=512 * 20,
        final_tokens=200 * len(pretrain_dataset) * block_size,
        num_workers=0,
    )
    trainer_obj = Trainer(model, pretrain_dataset, None, tconf, writer)
    ### END CODE HERE

    return tconf, trainer_obj

def train(model, writing_params_path, trainer_obj):
    ### TODO:
    ### - Given:
    ###     An output path writing_params_path for the model parameters
    ### [part c]:
    ###
    ### Note: trainer_obj is of type Trainer (see trainer.py for more details)
    ### START CODE HERE ###
    logging.info("Entering train function")
    if trainer_obj is None:
        logging.error("Trainer object is None. Cannot proceed with training.")
        return
    
    logging.info(f"Starting training with trainer_obj: {trainer_obj}")
    trainer_obj.train()
    torch.save(model.state_dict(), writing_params_path)
    logging.info(f"Model parameters saved to {writing_params_path}")
    ### END CODE HERE ###
    return