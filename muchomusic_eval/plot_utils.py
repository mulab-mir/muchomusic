import os
from math import pi

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def get_finegrained_results_df(path_to_results_csv):
    df = pd.read_csv(path_to_results_csv)
    for col in df.columns:
        if col != "eval_name":
            df[col] = df[col] * 100
    genre_columns = [
        "Reggae",
        "Electronic",
        "Latin",
        "Pop",
        "Blues",
        "Hip_Hop",
        "Folk_World_Country",
        "Funk_/_Soul",
        "Rock",
        "Jazz",
        "Classical",
    ]

    other_columns = df.columns.difference(genre_columns)
    other_df = df[other_columns]
    other_df.rename(
        columns={
            "temporal relations between elements": "Temporal \n Relations",
            "mood and expression": "Mood",
            "lyrics": "Lyrics",
            "historical and cultural context": "Cultural \n Context",
            "genre and style": "Genre",
            "functional context": "Functional \n Context",
            "melody": "Melody",
            "harmony": "Harmony",
            "metre and rhythm": "Metre & Rhythm",
            "structure": "Structure",
            "performance": "Performance",
            "instrumentation": "Instrumentation",
            "sound texture": "Sound \n Texture",
            "dynamics and expression": "Dynamics & Expression",
        },
        inplace=True,
    )
    other_df["Performance"] = (
        other_df["Dynamics & Expression"] + other_df["Performance"]
    ) / 2.0
    reorder = [
        "eval_name",
        "Metre & Rhythm",
        "Performance",
        "Instrumentation",
        "Cultural \n Context",
        "Lyrics",
        "Temporal \n Relations",
        "Functional \n Context",
        "Genre",
        "Mood",
        "Structure",
        "Harmony",
        "Melody",
        "Sound \n Texture",
        # "Dynamics & Expression",
    ]
    other_df = other_df[reorder]
    return other_df


def spider_plot(path_to_results_csv, output_dir):
    # number of variable
    df = get_finegrained_results_df(path_to_results_csv)
    categories = list(df)[1:]
    N = len(categories)

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # Initialise the spider plot
    ax = plt.subplot(111, polar=True)

    # If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels
    plt.xticks(angles[:-1], categories, size=15)
    ax.tick_params(
        axis="both",
        which="major",
        pad=40,
    )
    # plt.xticks(color=["red"] * 13, size=15)
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks(
        [0, 10, 20, 30, 40, 50, 60],
        ["0", "10", "20", "30", "40", "50", "60"],
        color="grey",
        size=10,
    )
    plt.ylim(0, 68)

    for row in range(len(df)):
        values = df.loc[row].drop("eval_name").values.flatten().tolist()
        print(values)
        values += values[:1]
        ax.plot(
            angles,
            values,
            linewidth=1,
            linestyle="solid",
            label=df.loc[row]["eval_name"],
        )
        ax.fill(angles, values, "r", alpha=0.1)

    colors = sns.color_palette("muted")

    locs, labels = plt.xticks()
    for lin in labels:
        if lin.get_text() in [
            "Cultural \n Context",
            "Lyrics",
            "Temporal \n Relations",
            "Functional \n Context",
            "Genre",
            "Mood",
        ]:
            # lin.set_text("Folk, World, Country")
            lin.set_color("#AF5958")
        else:
            lin.set_color("#406EB0")

    # Add legend
    plt.legend(loc="upper right", bbox_to_anchor=(-0.05, 0.15), fontsize=15)

    plt.savefig(
        os.path.join(output_dir, "spider_plot.png"),
        dpi=700,
        bbox_inches="tight",
    )
    # Show the graph
    plt.show()
