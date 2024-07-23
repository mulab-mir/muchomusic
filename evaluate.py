import argparse
import json
import os


from muchomusic_eval.scoring import (
    compare_answers,
    extract_responses,
    get_all_categories,
    get_finegrained_genre_scores,
    get_finegrained_knowledge_scores,
    get_finegrained_reasoning_scores,
    get_knowledge_scores,
    get_reasoning_scores,
)
from muchomusic_eval.utils import format_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/example_file.json")
    parser.add_argument("--output_dir", type=str, default="results")
    parser.add_argument("--save_results", action="store_false")
    parser.add_argument("--eval_name", type=str, default="default")
    args = parser.parse_args()

    with open(args.input) as f:
        eval_json = json.load(f)
    eval_json = {k: [dic[k] for dic in eval_json] for k in eval_json[0]}

    model_responses = eval_json["model_output"]
    prompts = eval_json["prompt"]
    answers = eval_json["answers"]
    answer_orders = eval_json["answer_orders"]

    extracted_responses = extract_responses(
        model_responses,
        answers,
    )

    reasoning_scores = get_reasoning_scores(
        extracted_responses,
        eval_json,
    )
    knowledge_scores = get_knowledge_scores(
        extracted_responses,
        eval_json,
    )
    scores = compare_answers(
        extracted_responses,
        answer_orders,
    )

    ########################
    # Finegrained results
    ########################
    all_genres, knowledge_categories, reasoning_categories = get_all_categories()

    all_genres = [i for i in all_genres if i in eval_json["genre"]]
    contained_knowledge_cats = [i for j in eval_json["knowledge"] for i in j]
    contained_reasoning_cats = [i for j in eval_json["reasoning"] for i in j]
    knowledge_categories = [
        i for i in knowledge_categories if i in contained_knowledge_cats
    ]
    reasoning_categories = [
        i for i in reasoning_categories if i in contained_reasoning_cats
    ]

    genre_finegrained_scores = get_finegrained_genre_scores(
        extracted_responses, eval_json, all_genres
    )
    reasoning_finegrained_scores = get_finegrained_reasoning_scores(
        extracted_responses, eval_json, reasoning_categories
    )
    knowledge_finegrained_scores = get_finegrained_knowledge_scores(
        extracted_responses, eval_json, knowledge_categories
    )

    all_genre_titles = [
        "_".join("".join("_".join(i.split(", ")).split("& ")).split(" "))
        for i in all_genres
    ]

    results = {
        "accuracy": scores["accuracy"],
        "IFR": scores["accuracy"],
        "knowledge": {
            "overall": knowledge_scores["accuracy"],
            "finegrained": {
                k: knowledge_finegrained_scores[k]["accuracy"]
                for k in knowledge_categories
            },
        },
        "reasoning": {
            "overall": reasoning_scores["accuracy"],
            "finegrained": {
                k: reasoning_finegrained_scores[k]["accuracy"]
                for k in reasoning_categories
            },
        },
    }

    format_dict(results)
    print(json.dumps(results, indent=4))

    # Update results csv
    if args.save_results:
        if not os.path.exists(args.output_dir):
            os.mkdir(args.output_dir)
        results_csv_path = os.path.join(args.output_dir, "results.csv")
        if not os.path.exists(results_csv_path):
            with open(results_csv_path, "w") as f:
                f.write(
                    f"eval_name,accuracy,unanswered_rate,reasonig_acc,knowledge_acc,{','.join(all_genre_titles)},{','.join(reasoning_categories)},{','.join(knowledge_categories)}\n"
                )
        with open(results_csv_path, "a") as f:
            f.write(
                f"{args.eval_name},{scores['accuracy']},{scores['unanswered_rate']},{knowledge_scores['accuracy']},{reasoning_scores['accuracy']},{','.join([str(genre_finegrained_scores[genre]['accuracy']) for genre in all_genres])},"
                f"{','.join([str(reasoning_finegrained_scores[reasoning]['accuracy']) for reasoning in reasoning_categories])},"
                f"{','.join([str(knowledge_finegrained_scores[knowledge]['accuracy']) for knowledge in knowledge_categories])}\n"
            )

        from muchomusic_eval.plot_utils import spider_plot

        spider_plot(results_csv_path, args.output_dir)
