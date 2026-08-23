import polars as pl
import numpy as np
import numpy.typing as npt
from typing import Any
from pyod.models.mcd import MCD
import plotly.express as px
import plotly.graph_objects as go

from src._registry.main import feathr


def maha_dist_plot(
    sorted_scores: npt.NDArray[Any],
    elbow_pct: float,
    elbow_cutoff: float,
    alpha: float,
    target_cutoff: float,
) -> go.Figure:
    title = f"Sorted Mahalanobis Distances<br>{elbow_pct=:.1%}, {elbow_cutoff=:.1f}, {alpha=:.1%}, {target_cutoff=:.1f}"
    fig = px.scatter(y=sorted_scores, title=title)
    fig.update_layout(xaxis_title=None, yaxis_title="Score")
    fig.update_layout(template="none")
    fig.add_hline(
        y=elbow_cutoff,
        line_dash="dash",
        line_color="red",
        line_width=2,
        annotation_text=" Elbow Cutoff",
        annotation_position="top left",
    )
    fig.add_hline(
        y=target_cutoff,
        line_dash="dot",
        line_color="purple",
        line_width=2,
        annotation_text=" Target Cutoff",
        annotation_position="top left",
    )
    return fig


def get_elbow_cutoff(sorted_scores: npt.NDArray[Any]) -> dict[str, float]:
    # 2. Get the Mahalanobis distances (decision scores) and sort them
    # PyOD stores the Mahalanobis distance in 'decision_scores_'
    n_points = len(sorted_scores)
    x_indices = np.arange(n_points)

    # 3. Draw a straight line between the first and last points
    # Coordinate of first point: (0, distances[0])
    # Coordinate of last point: (n_points-1, distances[-1])
    p1 = np.array([0, sorted_scores[0]])
    p2 = np.array([n_points - 1, sorted_scores[-1]])

    # 4. Calculate the distance from every point to this straight line
    # Formula for distance from point to line defined by two points (p1, p2)
    line_diff = p2 - p1
    line_len_sq = np.sum(line_diff**2)

    # Vector from p1 to all points on the curve
    points = np.vstack((x_indices, sorted_scores)).T
    vec_to_p1 = points - p1

    # Vector projection to find perpendicular distances
    scalar_proj = np.dot(vec_to_p1, line_diff) / line_len_sq
    projected_points = p1 + np.outer(scalar_proj, line_diff)
    perpendicular_distances = np.sqrt(np.sum((points - projected_points) ** 2, axis=1))

    # 5. Find the elbow
    elbow_index = np.argmax(perpendicular_distances)
    elbow_cutoff = sorted_scores[elbow_index]

    elbow_pct: float = len(sorted_scores[sorted_scores > elbow_cutoff]) / n_points

    return {"cutoff": elbow_cutoff, "pct": elbow_pct}


def get_target_cutoff(sorted_scores: npt.NDArray[Any], alpha) -> dict[str, float]:
    target_cutoff = np.percentile(sorted_scores, 100 * (1 - alpha))
    return {"cutoff": target_cutoff, "pct": alpha}


def set_outliers(
    data: pl.DataFrame, scores: npt.NDArray[Any], cutoff: float
) -> pl.DataFrame:
    data = data.with_columns(pl.lit(scores).alias("maha_score"))
    data = data.with_columns(pl.col("maha_score").gt(cutoff).alias("maha_outl"))
    return data


def main(table_nm: str = "sales") -> None:
    # How to tune the contaminaiton score: Find the point on the graph where the curve suddenly spikes upward. The percentage of points after that spike is your ideal contamination rate.

    data = feathr.load(table_nm)
    arr = data.select("sales_qty_lg", "sales_amt_lg").to_numpy()

    clf = MCD(contamination=0.1, random_state=42)
    clf.fit(arr)
    scores = clf.decision_scores_
    sorted_scores = np.sort(scores)
    elbow = get_elbow_cutoff(sorted_scores)
    target = get_target_cutoff(sorted_scores, alpha=0.10)
    fig = maha_dist_plot(
        sorted_scores,
        elbow_pct=elbow["pct"],
        elbow_cutoff=elbow["cutoff"],
        alpha=target["pct"],
        target_cutoff=target["cutoff"],
    )
    fig.show()
    data = set_outliers(data, scores=scores, cutoff=elbow["cutoff"])
    feathr.save(data, name=table_nm)
