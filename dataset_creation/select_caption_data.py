import ast
import csv
import json

import pandas as pd

AUDIOSET_ONTOLOGY = None


LOW_QUALITY_LABELS = [
    "bad quality audio",
    "bad audio quality",
    "bad quality recording",
    "inferior audio quality",
    "inferior sound quality",
    "inferior quality sound recording",
    "keyboard accompaniment poor audio quality",
    "low quality",
    "low quality recording",
    "low quality audio",
    "low audio quality",
    "poor quality audio",
    "poor audio quality",
    "low quality sound",
    "low quality audio recording",
    "poor audio-quality",
    "poorer audio-quality",
    "poor quality",
    "poor quality recording",
    "poor recording quality",
    "muddled audio",
    "muffled audio",
    "muffled sound",
    "low fidelity",
    "distorted audio",
    "lo-res",
    #    "amateur recording",
    #    "home recording",
    #    "amateur video",
    #    "average audio quality",
]


def load_musiccaps_balanced_subset(path):
    # Load the data
    mc_df = pd.read_csv(path)
    mc_df = mc_df[mc_df["is_balanced_subset"]]
    mc_df.drop(columns=["is_balanced_subset", "is_audioset_eval"], inplace=True)
    mc_df["aspect_list"] = mc_df["aspect_list"].apply(ast.literal_eval)
    mc_df["audioset_positive_labels"] = mc_df["audioset_positive_labels"].str.split(",")
    mc_df["audioset_positive_labels"] = mc_df["audioset_positive_labels"].apply(
        map_audioset_labels
    )
    return mc_df


def get_audioset_ontology_singleton():
    global AUDIOSET_ONTOLOGY
    if AUDIOSET_ONTOLOGY is None:
        AUDIOSET_ONTOLOGY = pd.read_json(
            "https://raw.githubusercontent.com/audioset/ontology/master/ontology.json"
        ).set_index("id")
    return AUDIOSET_ONTOLOGY


def map_audioset_labels(labels):
    # /m/04rlf is the root label 'Music'
    ontology_singleton = get_audioset_ontology_singleton()
    return [
        ontology_singleton.loc[label]["name"] for label in labels if label != "/m/04rlf"
    ]


def load_musiccaps_genre_annotations(path):
    genre_preds_df = pd.read_csv(path).set_index("name")
    genre_preds_df.index = genre_preds_df.index.str.rsplit(".", n=1).str[0]
    genre_preds_df.reset_index(inplace=True)
    genre_preds_df["start"] = genre_preds_df["name"].str.rsplit("_", n=1).str[1]
    genre_preds_df["name"] = genre_preds_df["name"].str.rsplit("_", n=1).str[0]
    genre_preds_df.set_index(["name", "start"], inplace=True)
    genres = genre_preds_df.idxmax(axis=1)
    genres = genres.str.split("---").str[0]
    return genres


def remove_by_matching_labels(df, labels, column):
    return df[
        ~df[column].apply(lambda annotated: any(label in annotated for label in labels))
    ]


def map_jamendo_annotations(annotations: list[str]) -> list[str]:
    mapped = []
    for annotation in annotations:
        task, labels = annotation.split("---")
        label = labels.split(",")[0]
        if task == "tonal_atonal":
            continue  # all seem to have `tonal` as annotation
        if task == "gender":
            if label == "instrumental":
                continue  # no singer gender
            else:
                task = "singer_gender"
        mapped.append(": ".join((task, label)))
    return mapped


def load_song_describer_data_for_generation(
    sdd_path="data/SongDescriberDataset/song_describer.csv",
    tag_annotations_path="data/SongDescriberDataset/music-classification-annotations-clean.tsv",
):
    sdd_df = pd.read_csv(sdd_path, dtype={"track_id": str})
    sdd_df = sdd_df.set_index("caption_id")
    annotations = {}
    with open(tag_annotations_path, newline="") as fh:
        reader = csv.DictReader(
            fh,
            fieldnames=["track", "artist", "album", "path", "duration", "annotations"],
            restkey="extra",
            delimiter="\t",
        )
        next(reader)  # skip header
        for row in reader:
            track_id = row["track"].removeprefix("track_")
            annotation_labels = map_jamendo_annotations(
                [row["annotations"]] + row.get("extra", [])
            )
            annotations[track_id] = json.dumps(annotation_labels)
        annotations = pd.DataFrame.from_dict(
            annotations, orient="index", columns=["aspects"]
        )
    sdd_df = pd.merge(
        sdd_df, annotations, left_on="track_id", right_index=True, how="left"
    )
    multiple_cap = sdd_df.groupby("track_id").count()["caption"] >= 2
    track_ids_to_keep = multiple_cap[multiple_cap].index.tolist()
    sdd_df = sdd_df[sdd_df["track_id"].isin(track_ids_to_keep)]
    sdd_df["aspects"] = sdd_df["aspects"].fillna("[]")
    sdd_df["aspects"] = sdd_df["aspects"].apply(json.loads)
    return sdd_df


def load_mtg_jamendo_genre_annotations(path):
    mtg_genres_df = pd.read_csv(path, sep="\t", index_col=0)
    mtg_genres_df.index = mtg_genres_df.index.str[3:]
    non_genre_columns = mtg_genres_df.columns[
        ~mtg_genres_df.columns.str.startswith("genre_")
    ]
    mtg_genres_df.drop(columns=non_genre_columns.tolist(), inplace=True)
    mtg_genres_df = mtg_genres_df.rename(
        columns=lambda x: x.replace("genre_discogs400-discogs-effnet-1---", "")
    )
    genres = mtg_genres_df.idxmax(axis=1)
    genres = genres.str.split("---").str[0]
    return genres.rename("genre")
