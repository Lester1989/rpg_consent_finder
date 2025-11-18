from nicegui import ui
import pandas as pd
import numpy as np
from matplotlib.axes import Axes

from localization.language_manager import get_localization
from models.db_models import PlayFunResult
from services.session_service import session_storage


def radar_plot(
    categories: list[str],
    data_series_list: list[list[float]],
    ax: Axes,
    series_names: list[str],
    title="Radar Plot",
):
    """
    Creates a radar plot with multiple data series.

    Args:
        categories (list): List of category labels.
        data_series_list (list of lists): List of data series, each a list of values.
        ax (matplotlib.axes.Axes): Axes object to plot on.
        series_names (list): List of series names.
        title (str): Title of the plot.
    """

    n = len(categories)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]  # Close the circle

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        categories,
        color="lightgray",
        fontsize=9,
        ha="center",
        va="center",
        position=(0, -0.1),
    )  # Adjusted position

    ax.set_title(title, size=10, y=1.1, color="lightgray")
    ax.set_facecolor("#1f2937")
    ax.tick_params(colors="lightgray")
    ax.spines["polar"].set_color("lightgray")

    colors = [
        "lightblue",
        "lightgreen",
        "lightcoral",
        "gold",
    ]  # Define colors for each series
    for i, values in enumerate(data_series_list):
        values_closed = values + values[:1]  # Close the circle
        ax.plot(
            angles,
            values_closed,
            linewidth=2,
            linestyle="solid",
            marker="o",
            color=colors[i % len(colors)],
            label=series_names[i],
        )
        ax.fill(angles, values_closed, alpha=0.25, color=colors[i % len(colors)])

    ax.set_rgrids(
        np.arange(1, max(max(series) for series in data_series_list) + 1),
        color="lightgray",
        alpha=0.5,
    )  # Added rgrids
    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.3, 1.1),
        fontsize="small",
        framealpha=0.5,
        facecolor="#333",
        edgecolor="lightgray",
        labelcolor="lightgray",
    )  # Added legend


class PlayfunPlot(ui.card):
    def __init__(
        self,
        datas: list[PlayFunResult] | dict[str, PlayFunResult],
        **kwargs,
    ):
        super().__init__(**kwargs)
        lang = session_storage.get("lang", "en")
        data = {"categories": PlayFunResult.categories(lang)}
        if not datas:
            ui.label(get_localization("no_data"))
            return
        if isinstance(datas, dict):
            data |= {key: list(data.ratings.values()) for key, data in datas.items()}
        else:
            data |= {data.user.nickname: list(data.ratings.values()) for data in datas}
        df = pd.DataFrame(data)
        with self.classes("w-auto bg-gray-800"):
            with ui.matplotlib(figsize=(9, 7)).figure as fig:
                fig.patch.set_facecolor("#1f2937")
                ax = fig.add_subplot(111, polar=True)

                series_names = [col for col in df.columns if col != "categories"]
                data_series_list = [df[col].tolist() for col in series_names]

                radar_plot(
                    df["categories"],
                    data_series_list,
                    ax,
                    series_names,
                    title=get_localization("playfun_plot_title"),
                )
