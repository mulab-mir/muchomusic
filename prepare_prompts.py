import argparse
import ast
import json
import random

import yaml

from muchomusic.utils import get_all_audio_paths, load_questions_from_csv


def _shuffle_answers(questions, answers):
    """Shuffle order of the answer options."""
    num_answers = len(answers[0])
    answer_orders = [
        random.sample(range(num_answers), k=num_answers) for i in range(len(questions))
    ]
    shuffled_answers = [
        [answers[i][j] for j in answer_orders[i]] for i in range(len(questions))
    ]
    return shuffled_answers, answer_orders


def get_prompts(questions, answers, in_context_expamples: list[str]):
    questions_with_options = []
    letter_options = ["A", "B", "C", "D"]
    for i, question in enumerate(questions):
        if in_context_expamples:
            question_with_options = (
                " ".join(in_context_expamples)
                + "\n Question: "
                + question
                + "\n Options: "
            )
        else:
            question_with_options = "Question: " + question + "\n Options: "
        for j in range(len(answers[i])):
            question_with_options += f"({letter_options[j]}) {answers[i][j]} "
        question_with_options += "\n The correct answer is: "
        questions_with_options.append(question_with_options)
    return questions_with_options


def prepare_questions(
    questions_path,
    in_context_examples=None,
    option_subset=None,
    distractors=[
        "incorrect_but_related",
        "correct_but_unrelated",
        "incorrect_and_unrelated",
    ],
):
    (
        ids,
        questions,
        answers,
        datasets,
        genres,
        reasoning,
        knowledge,
    ) = load_questions_from_csv(questions_path, distractors=distractors)
    if option_subset is not None:
        assert 0 in option_subset
        answers = [answers[i] for i in option_subset]
    answers, answer_orders = _shuffle_answers(questions, answers)
    prompts = get_prompts(questions, answers, in_context_examples)

    reasoning = [ast.literal_eval(item) for item in reasoning]
    knowledge = [ast.literal_eval(item) for item in knowledge]

    return {
        "id": ids,
        "prompt": prompts,
        "answers": answers,
        "answer_orders": answer_orders,
        "dataset": datasets,
        "genre": genres,
        "reasoning": reasoning,
        "knowledge": knowledge,
    }


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="default")
    parser.add_argument("--output_path", type=str, default="example_file.json")

    args = parser.parse_args()

    with open(
        f"muchomusic/configs/{args.config}.yaml",
        "r",
    ) as file:
        exp_config = yaml.safe_load(file)

    question_dict = prepare_questions(
        questions_path="data/muchomusic.csv",
        in_context_examples=exp_config["in_context_examples"],
        distractors=exp_config["distractors"],
    )

    audio_file_paths = get_all_audio_paths(
        question_dict["id"],
        question_dict["dataset"],
    )
    question_dict["audio_path"] = audio_file_paths

    question_dict["model_output"] = ["A"] * len(audio_file_paths)

    inputs_dict = [
        dict(
            zip(
                question_dict,
                t,
            )
        )
        for t in zip(*question_dict.values())
    ]

    with open(args.output_path, "w") as f:
        json.dump(inputs_dict, f)
