import json
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


def get_audio_path_from_id(audio_id, df, dataset="sdd"):
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


def load_questions_from_json(questions_path, distractors):
    with open(questions_path, "r") as file:
        json_data = json.load(file)
    ids = []
    questions = []
    answers = []
    explanations = []
    if "0312sdd_questions.json" in questions_path or "gemini" in questions_path:
        items = list(json_data.values())
        for audio_id, items in json_data.items():
            if "gemini" in questions_path:
                if "sdd" in questions_path:
                    audio_id = int(audio_id.removesuffix(".json"))
                elif "mc" in questions_path:
                    audio_id = audio_id.removesuffix(".json")
                    audio_id = "_".join(audio_id.split("_")[:-1])
            for question_data in items["questions"]:
                answer_list = []
                ids.append(audio_id)
                questions.append(question_data["question"])
                correct_answer = question_data["correct_answer"]
                answer_list.append(correct_answer)
                if "incorrect_but_related" in distractors:
                    incorrect_but_related = question_data["distractors"][
                        "incorrect_but_related"
                    ]["distractor"]
                    answer_list.append(incorrect_but_related)
                if "correct_but_unrelated" in distractors:
                    correct_but_unrelated = question_data["distractors"][
                        "correct_but_unrelated"
                    ]["distractor"]
                    answer_list.append(correct_but_unrelated)
                if "incorrect_and_unrelated" in distractors:
                    incorrect_and_unrelated = question_data["distractors"][
                        "incorrect_and_unrelated"
                    ]["distractor"]
                    answer_list.append(incorrect_and_unrelated)
                answers.append(answer_list)
    else:
        for item in json_data:
            if "sdd_questions_sample.json" in questions_path:
                questions_data = item[1]["questions"]
                for question_data in questions_data:
                    ids.append(item[0])
                    questions.append(question_data["question"])
                    if len(question_data["answers"]) == 1:
                        answers.append(list(question_data["answers"][0].values()))
                    elif len(question_data["answers"]) > 1:
                        answers.append(
                            [list(i.values())[0] for i in question_data["answers"]]
                        )
                    explanations.append(question_data["explanation"])
            if "0311sdd_questions.json" in questions_path:
                questions_data = item[1]["questions"]
                for question_data in questions_data:
                    ids.append(item[0])
                    questions.append(question_data["question"])
                    correct_answer = question_data["correct_answer"]
                    incorrect_but_related = question_data["distractors"][
                        "incorrect_but_related"
                    ]["distractor"]
                    correct_but_unrelated = question_data["distractors"][
                        "correct_but_unrelated"
                    ]["distractor"]
                    incorrect_and_unrelated = question_data["distractors"][
                        "incorrect_and_unrelated"
                    ]["distractor"]
                    answers.append(
                        [
                            correct_answer,
                            incorrect_but_related,
                            correct_but_unrelated,
                            incorrect_and_unrelated,
                        ]
                    )
    return ids, questions, answers, explanations

def format_dict(d, decimal_places=2):
    for key, value in d.items():
        if isinstance(value, dict):
            format_dict(value, decimal_places)
        elif isinstance(value, float):
            d[key] = round(value, decimal_places)
