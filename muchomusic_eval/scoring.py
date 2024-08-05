import ast

import pandas as pd


def extract_responses(
    model_outputs,
    answer_options,
    prefix="The correct answer is:",
    letter_options=["A", "B", "C", "D"],
):
    """Map the model output to the selected option.

    Extract the letter corresponding to the answer selected by the model by
    simply checking:
    1. If one (and only one) of the letter options is mentioned in the response.
    2. If the normalised text in the response is contained in the normalised text
    of one of the answer options.
    Prior to checking the above, the prefix is removed from the model output.
    """
    responses = []
    for i, output in enumerate(model_outputs):
        output = output.split(prefix)[-1].strip()
        response = list(set(letter_options).intersection(output))
        if len(response) == 1:
            responses.append(letter_options.index(response[0]))
        else:
            normalized_output = output.lower().strip()
            normalized_answers = [j.lower().strip() for j in answer_options[i]]
            for j, answer in enumerate(normalized_answers):
                if answer in normalized_output:
                    responses.append(j)
                    break
            else:
                responses.append(-1)
    return responses


def compare_answers(responses, answer_orders):
    """Compare model answers to ground truth."""
    num_correct = 0
    for a, b in zip(responses, answer_orders):
        if a == b.index(0):
            num_correct += 1
    num_unanswered = len([i for i in responses if i == -1])
    return {
        "total_questions": len(responses),
        "correct": num_correct,
        "accuracy": num_correct / len(responses),
        "unanswered": num_unanswered,
        "unanswered_rate": num_unanswered / len(responses),
    }


def get_reasoning_scores(extracted_responses, question_dict):
    reasoning_scores = compare_answers(
        [
            response
            for i, response in enumerate(extracted_responses)
            if question_dict["reasoning"][i] != []
        ],
        [
            answer_order
            for i, answer_order in enumerate(question_dict["answer_orders"])
            if question_dict["reasoning"][i] != []
        ],
    )
    return reasoning_scores


def get_knowledge_scores(extracted_responses, question_dict):
    knowledge_scores = compare_answers(
        [
            response
            for i, response in enumerate(extracted_responses)
            if question_dict["knowledge"][i] != []
        ],
        [
            answer_order
            for i, answer_order in enumerate(question_dict["answer_orders"])
            if question_dict["knowledge"][i] != []
        ],
    )
    return knowledge_scores


def get_finegrained_reasoning_scores(
    extracted_responses,
    question_dict,
    reasoning_categories,
):
    reasoning_scores = {}
    for reasoning_cat in reasoning_categories:
        reasoning_scores[reasoning_cat] = compare_answers(
            [
                response
                for i, response in enumerate(extracted_responses)
                if reasoning_cat in question_dict["reasoning"][i]
            ],
            [
                answer_order
                for i, answer_order in enumerate(question_dict["answer_orders"])
                if reasoning_cat in question_dict["reasoning"][i]
            ],
        )
    return reasoning_scores


def get_finegrained_knowledge_scores(
    extracted_responses,
    question_dict,
    knowledge_categories,
):
    knowledge_scores = {}
    for knowledge_cat in knowledge_categories:
        knowledge_scores[knowledge_cat] = compare_answers(
            [
                response
                for i, response in enumerate(extracted_responses)
                if knowledge_cat in question_dict["knowledge"][i]
            ],
            [
                answer_order
                for i, answer_order in enumerate(question_dict["answer_orders"])
                if knowledge_cat in question_dict["knowledge"][i]
            ],
        )
    return knowledge_scores


def get_finegrained_genre_scores(
    extracted_responses,
    question_dict,
    all_genres,
):
    genre_scores = {}
    for genre in all_genres:
        genre_scores[genre] = compare_answers(
            [
                response
                for i, response in enumerate(extracted_responses)
                if question_dict["genre"][i] == genre
            ],
            [
                answer_order
                for i, answer_order in enumerate(question_dict["answer_orders"])
                if question_dict["genre"][i] == genre
            ],
        )
    return genre_scores


def get_all_categories():
    benchmark = pd.read_csv("data/muchomusic.csv")
    all_genres = benchmark["genre"].tolist()
    knowledge_categories = benchmark["music_knowledge"].tolist()
    reasoning_categories = benchmark["music_reasoning"].tolist()

    def flatten_list(original_list):
        flat_list = [
            item
            for sublist in original_list
            if isinstance(sublist, str)
            for item in ast.literal_eval(sublist)
        ]
        return flat_list

    all_genres = set(all_genres)
    knowledge_categories = list(set(flatten_list(knowledge_categories)))
    reasoning_categories = list(set(flatten_list(reasoning_categories)))
    return all_genres, knowledge_categories, reasoning_categories
