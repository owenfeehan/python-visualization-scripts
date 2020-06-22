from typing import Optional

from projection import Projection
from features import LabelledFeatures
from .visualize_features_scheme import VisualizeFeaturesScheme
import os
import tensorflow as tf
import pandas as pd
import csv
from tensorboard.plugins import projector


class TensorBoardExport(VisualizeFeaturesScheme):
    """Exports features (and optional image sprites) in a format so that TensorBoard can be used for visualization"

    Thanks to the TensorBoard tutorial
    https://www.tensorflow.org/tensorboard/tensorboard_projector_plugin

    Thanks to a medium.com post by Andrew B. Martin for the inspiration
    https://medium.com/looka-engineering/how-to-visualize-feature-vectors-with-sprites-and-tensorflows-tensorboard-3950ca1fb2c7
    """

    def __init__(self, projection: Optional[Projection], output_path: str):
        """Constructor

        :param projection: optional projection to reduce dimensionality before export
        :param output_path: where to write the "log-dir" for tensorboard
        """
        self._projection = projection
        self._output_path = _create_dir_or_throw(output_path)

    def visualize_data_frame(self, features: LabelledFeatures) -> None:

        print("Exporting tensorboard logs to: {}".format(self._output_path))

        path_metadata = self._resolved_path('metadata.tsv')
        path_checkpoint = self._resolved_path('features.ckpt')

        _write_labels(features.labels, path_metadata)
        _save_embedding_as_checkpoint(
            self._maybe_project(features.df_features),
            path_checkpoint
        )

        projector.visualize_embeddings(
            self._output_path,
            _create_projector_config(path_metadata)
        )

    def _maybe_project(self, df: pd.DataFrame) -> pd.DataFrame:
        if self._projection is not None:
            return self._projection.project(df)
        else:
            return df

    def _resolved_path(self, path_relative_to_log_dir: str) -> str:
        """Resolves a path to the log-dir

        :param path_relative_to_log_dir a path expressed relative only to the log dir
        :return an absolute path
        """
        return os.path.join(self._output_path, path_relative_to_log_dir)


def _create_projector_config(path: str) -> projector.ProjectorConfig:
    """Creates a projector-config as needed to show the embedding in Tensorboard"""
    config = projector.ProjectorConfig()
    embedding = config.embeddings.add()
    embedding.tensor_name = "embedding/.ATTRIBUTES/VARIABLE_VALUE"
    embedding.metadata_path = path
    return config


def _save_embedding_as_checkpoint(embedding: pd.DataFrame, path: str) -> None:
    """Saves the feature embedding as a checkpointed tensor"""
    weights = tf.Variable(tf.convert_to_tensor(embedding.to_numpy()))
    checkpoint = tf.train.Checkpoint(embedding=weights)
    checkpoint.save(path)


def _write_labels(labels: pd.Series, path: str) -> None:
    """Writes each label on a separate line to a file"""
    labels.to_csv(path, sep="\t", header=["Label"], index=True, index_label="Identifier")


def _create_dir_or_throw(path: Optional[str]) -> str:
    """Creates a directory if necessary and if defined. If not defined, throw an exception."""
    if path is not None:
        # Make the directory if necessary
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    else:
        raise Exception("An output-path must be specified for the TensorBoard method")
