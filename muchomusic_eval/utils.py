import os

import pandas as pd


def get_all_audio_paths(audio_ids, datasets):
    path_to_sdd = os.path.join("data", "sdd")
    sdd_df = pd.read_csv(os.path.join(path_to_sdd, "song_describer.csv"))
    path_to_mc = os.path.join("data", "musiccaps")
    mc_df = pd.read_csv(os.path.join(path_to_mc, "musiccaps-public.csv"))

    audio_paths = []
    for audio_id, dataset in zip(audio_ids, datasets):
        if dataset == "sdd":
            audio_path = os.path.join(
                path_to_sdd,
                "audio",
                sdd_df.loc[sdd_df["track_id"] == int(audio_id)]["path"]
                .values[0]
                .replace(".mp3", ".2min.mp3"),
            )
            audio_paths.append(audio_path)
        elif dataset == "musiccaps":
            instance = mc_df.loc[mc_df["ytid"] == audio_id].iloc[0]
            audio_path = (
                f"[{instance.ytid}]-[{int(instance.start_s)}-{int(instance.end_s)}].wav"
            )
            audio_path = os.path.join(path_to_mc, "audio", audio_path)
            audio_paths.append(audio_path)
    return audio_paths


def get_audio_path_from_id(audio_id, dataset="sdd"):
    if dataset == "sdd":
        path_to_dataset = os.path.join("data", "sdd")
        df = pd.read_csv(os.path.join(path_to_dataset, "song_describer.csv"))
        audio_path = os.path.join(
            path_to_dataset,
            "audio",
            df.loc[df["track_id"] == int(audio_id)]["path"]
            .values[0]
            .replace(".mp3", ".2min.mp3"),
        )
    elif dataset == "musiccaps":
        path_to_dataset = os.path.join("data", "musiccaps")
        df = pd.read_csv(os.path.join(path_to_dataset, "musiccaps-public.csv"))
        instance = df.loc[df["ytid"] == audio_id].iloc[0]
        audio_path = (
            f"[{instance.ytid}]-[{int(instance.start_s)}-{int(instance.end_s)}].wav"
        )
        audio_path = os.path.join(path_to_dataset, "audio", audio_path)
    return audio_path


def load_questions_from_csv(question_path, distractors):
    df = pd.read_csv(question_path)
    questions = df["question"].tolist()
    datasets = df["dataset"].tolist()
    reasoning = df["music_reasoning"].fillna("[]")
    knowledge = df["music_knowledge"].fillna("[]")
    genres = df["genre"].fillna("").tolist()
    answers = []
    audio_ids = []

    for row in df.iterrows():
        answer_list = []
        audio_id = row[1]["dataset_identifier"]
        if row[1]["dataset"] == "sdd":
            audio_id = int(audio_id.removesuffix(".json"))
        else:
            audio_id = audio_id.removesuffix(".json")
            audio_id = "_".join(audio_id.split("_")[:-1])
        audio_ids.append(audio_id)
        answer_list.append(row[1]["correct_answer"])
        if "incorrect_but_related" in distractors:
            answer_list.append(row[1]["distractor_1_answer"])
        if "correct_but_unrelated" in distractors:
            answer_list.append(row[1]["distractor_2_answer"])
        if "incorrect_and_unrelated" in distractors:
            answer_list.append(row[1]["distractor_3_answer"])
        answers.append(answer_list)

    return audio_ids, questions, answers, datasets, genres, reasoning, knowledge


def format_dict(d, decimal_places=2):
    for key, value in d.items():
        if isinstance(value, dict):
            format_dict(value, decimal_places)
        elif isinstance(value, float):
            d[key] = round(value, decimal_places)
