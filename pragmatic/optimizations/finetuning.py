from datasets import load_dataset, Dataset
from sentence_transformers import (
    SentenceTransformer,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
)
from sentence_transformers.losses import CoSENTLoss

import os
from typing import Union, Dict


def finetune_embedding_model(settings):
    model = SentenceTransformer(settings["initial_embedding_model_path"])

    # we assume each dataset entry to contain a pair of sentences and a float similarity score
    dataset = load_dataset_from_source(settings["embedding_model_finetuning_dataset_path"],
                                       settings["embedding_model_finetuning_dataset_subset_name"])

    loss = CoSENTLoss(model)

    finetuning_args = SentenceTransformerTrainingArguments(output_dir=os.path.dirname(settings["embedding_model_path"]),
                                                           **settings["embedding_model_finetuning_parameters"])

    trainer = SentenceTransformerTrainer(model=model, train_dataset=dataset, loss=loss, args=finetuning_args)
    trainer.train()

    model.save_pretrained(settings["embedding_model_path"])


def load_dataset_from_source(data_source: Union[str, Dict[str, list]], subset: str = None) -> Dataset:
    if isinstance(data_source, str):
        if os.path.isfile(data_source):
            # the dataset is a local CSV or JSON file
            try:
                dataset = load_dataset('csv', data_files=data_source)
                return dataset
            except Exception:
                try:
                    dataset = load_dataset('json', data_files=data_source)
                    return dataset
                except Exception as e:
                    raise ValueError(f"Error loading local file {data_source}: {e}")

        # the dataset is a Huggingface dataset
        try:
            if subset is not None:
                dataset = load_dataset(data_source, subset)
            else:
                dataset = load_dataset(data_source)
            return dataset['train'] if 'train' in dataset else dataset
        except Exception as e:
            raise ValueError(f"Error loading Huggingface dataset {data_source}: {e}")

    if isinstance(data_source, dict):
        # the dataset is a Python dictionary
        try:
            dataset = Dataset.from_dict(data_source)
            return dataset
        except Exception as e:
            raise ValueError(f"Error converting dictionary to dataset: {e}")

    raise ValueError(f"Unsupported data source type {type(data_source)}. Please provide a string or a dictionary.")
