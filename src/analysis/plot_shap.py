from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib.pyplot as plt

import numpy as np

from typing import Dict, List, Tuple, Optional


int2month = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}


def plot_shap_values(x: np.ndarray,
                     shap_values: np.ndarray,
                     val_list: List[str],
                     normalizing_dict: Dict[str, Dict[str, float]],
                     value_to_plot: str,
                     normalize_shap_plots: bool = True,
                     show: bool = False,
                     polished_value_name: Optional[str] = None,
                     pred_date: Optional[Tuple[int, int]] = None) -> None:
    """Plots the denormalized values against their shap values, so that
    variations in the input features to the model can be compared to their effect
    on the model. For example plots, see notebooks/08_gt_recurrent_model.ipynb.
    Parameters:
    ----------
    x: np.array
        The input to a model for a single data instance
    shap_values: np.array
        The corresponding shap values (to x)
    val_list: list
        A list of the variable names, for axis labels
    normalizing_dict: dict
        The normalizing dict saved by the `Engineer`, so that the x array can be
        denormalized
    value_to_plot: str
        The specific input variable to plot. Must be in val_list
    normalize_shap_plots: bool = True
        If True, then the scale of the shap plots will be uniform across all
        variable plots (on an instance specific basis).
    show: bool = False
        If True, a plot of the variable `value_to_plot` against its shap values will be plotted.
    polished_value_name: Optional[str] = None
        If passed to the model, this is used instead of value_to_plot when labelling the axes.
    pred_month: Optional[Tuple[int, int]] = None
        If passed to the model, the x axis will contain actual months instead of the index.
        Note the tuple is [int_month, int_year]
    """
    # first, lets isolate the lists
    idx = val_list.index(value_to_plot)

    x_val = x[:, idx]

    # we also want to denormalize
    for norm_var in normalizing_dict.keys():
        if value_to_plot.endswith(norm_var):
            x_val = (x_val * normalizing_dict[norm_var]['std']) + \
                normalizing_dict[norm_var]['mean']
            break

    shap_val = shap_values[:, idx]

    months = list(range(1, len(x_val) + 1))

    if pred_date is not None:
        int_months, int_years = [], []
        cur_month, cur_year = pred_date[0], pred_date[1]
        for i in range(1, len(x_val) + 1):
            cur_month = cur_month - 1
            if cur_month == 0:
                cur_month = 12
                cur_year -= 1
            int_months.append(cur_month)
            int_years.append(cur_year)
        str_dates = [f'{int2month[m]} {y}' for m, y in zip(int_months, int_years)][::-1]

    host = host_subplot(111, axes_class=AA.Axes)
    plt.subplots_adjust(right=0.75)

    par1 = host.twinx()
    par1.axis["right"].toggle(all=True)

    if normalize_shap_plots:
        par1.set_ylim(shap_values.min(), shap_values.max())

    if polished_value_name is None:
        polished_value_name = value_to_plot

    host.set_xlabel("Months")
    host.set_ylabel(polished_value_name)
    par1.set_ylabel("Shap value")

    p1, = host.plot(months, x_val, label=polished_value_name)
    p2, = par1.plot(months, shap_val, label="shap value")

    host.axis["left"].label.set_color(p1.get_color())
    par1.axis["right"].label.set_color(p2.get_color())

    host.legend(loc=2)

    if pred_date is not None:
        modulo = (len(months) - 1) % 2
        host.set_xticks(months[modulo::2])
        host.set_xticklabels(str_dates[modulo::2])

    plt.draw()
    if show:
        plt.show()
