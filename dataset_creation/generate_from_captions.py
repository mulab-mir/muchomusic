import ast
import json

import pandas as pd


def read_json_response(response):
    response = response.removeprefix("```json\n").removeprefix("```JSON\n").removesuffix("\n```")
    response = response.strip("`")
    return json.loads(response)


def build_sdd_prompt(track_id, df):
    matching_rows = df[df["track_id"] == track_id]
    descriptions = "DESCRIPTIONS\n* " + "\n* ".join(matching_rows["caption"].tolist())
    if aspects := matching_rows.iloc[0]["aspects"]:
        tags = "TAGS\n* " + "\n* ".join(aspects)
    else:
        tags = ""
    return "\n\n".join((descriptions, tags))


def build_mc_prompt(row):
    descriptions = "DESCRIPTIONS \n" + row["caption"]
    tags = "TAGS\n* " + "\n* ".join(row["tags"])
    return "\n\n".join((descriptions, tags))


def load_mc_data_for_generation(mc_data_path):
    musiccaps_df = pd.read_csv(mc_data_path)
    musiccaps_df["aspect_list"] = musiccaps_df["aspect_list"].apply(ast.literal_eval)
    musiccaps_df["audioset_positive_labels"] = musiccaps_df["audioset_positive_labels"].apply(ast.literal_eval)
    musiccaps_df["tags"] = musiccaps_df["aspect_list"] + musiccaps_df["audioset_positive_labels"]
    return musiccaps_df
