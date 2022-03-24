import pandas as pd
import matplotlib.cm as cm
import numpy as np
import matplotlib.pyplot as plt


def plot_clustered_stacked(dfall, labels=None, title="Localizations", H="-", **kwargs):
    """Given a list of dataframes, with identical columns and index, create a clustered stacked bar plot.
labels is a list of the names of the dataframe, used for the legend
title is a string for the title of the plot
H is the hatch used for identification of the different dataframe"""

    n_df = len(dfall)
    n_col = len(dfall[0].columns)
    n_ind = len(dfall[0].index)
    axe = plt.subplot(111)

    colors = ["blue", "coral", "slategray"]
    hatches = ["-", "o", ""]

    uu = 0
    for df in dfall:  # for each data frame
        axe = df.plot(kind="bar",
                      linewidth=0,
                      stacked=True,
                      ax=axe,
                      legend=False,
                      grid=False,
                      color=colors[uu],
                      **kwargs)  # make bar plots
        uu += 1

    h, l = axe.get_legend_handles_labels()  # get the handles we want to modify
    for i in range(0, n_df * n_col, n_col):  # len(h) = n_col * n_df
        for j, pa in enumerate(h[i:i + n_col]):
            for rect in pa.patches:  # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
                rect.set_hatch(hatches[j])  # edited part
                rect.set_width(1 / float(n_df + 1))

    axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    axe.set_xticklabels(df.index, rotation=0)
    axe.set_title(title)

    axe.set_xlabel("Fault Types")
    axe.set_ylabel("%")

    # Add invisible data to add another legend
    n = []
    for i in range(n_df):
        n.append(axe.bar(0, 0, color=colors[i]))

    l1 = axe.legend(h[:n_col], l[:n_col], loc=[1.01, 0.5])
    if labels is not None:
        l2 = plt.legend(n, labels, loc=[1.01, 0.1])
    axe.add_artist(l1)
    plt.show()
    return axe


df_curix = pd.read_csv("resources/data/11-localizations-data-frames/DF-Curix.csv", index_col=0)
df_embed = pd.read_csv("resources/data/11-localizations-data-frames/DF-Embed.csv", index_col=0)
df_premise = pd.read_csv("resources/data/11-localizations-data-frames/DF-Premise.csv", index_col=0)

print(df_curix.head(10))
print(df_embed.head(10))
print(df_premise.head(10))

plot_clustered_stacked([df_curix, df_embed, df_premise], ["Prevent", "Embed", "Premise"])
