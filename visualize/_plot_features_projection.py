"""A scheme for visualizing features involving a projection into an embedding and plotting"""
from typing import Optional

import pandas as pd
import plotly.express as px

from features import LabelledFeatures
from projection import Projection
from .visualize_features_scheme import VisualizeFeaturesScheme


class PlotFeaturesProjection(VisualizeFeaturesScheme):
    """Projects the feature space onto two dimensions and plots"""
    def __init__(self, projection: Projection):
        """Constructor

        :param projection how the projection is performed
        """
        if projection is None:
            raise Exception("A projection is required for {}".format(self.__class__.__name__))

        self._projection = projection

    def visualize_data_frame(self, features: LabelledFeatures) -> None:

        df_projected = self._projection.project(features.features)

        _plot_first_two_dims_projection(df_projected, features.labels)


def _plot_first_two_dims_projection(df: pd.DataFrame, labels: Optional[pd.Series] = None) -> None:

    # Makes the identifiers a normal column (to see the identifier when hovering over a point in plotly)
    df["identifier"] = df.index

    if labels is not None:
        df["label"] = labels

    fig = px.scatter(
        df,
        x=df.columns[0],
        y=df.columns[1],
        color="label" if labels is not None else None,
        hover_name="identifier"
    )
    fig.show()
