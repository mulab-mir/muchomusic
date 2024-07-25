<div  align="center">

# MuChoMusic: Evaluating Music Understanding in Multimodal Audio-Language Models
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)
[![arXiv](https://img.shields.io/badge/arXiv-0000.0000-<COLOR>.svg)]() 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12709974.svg)](https://doi.org/10.5281/zenodo.12709974)
[![Huggingface](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Datasets-yellow)](https://huggingface.co/datasets/mulab-mir/muchomusic)

[Benno Weck](https://www.upf.edu/web/mtg/about/team-members/-/asset_publisher/l2XuyhfmWvQ5/content/weck-benno/maximized)\*<sup>1</sup>, 
[Ilaria Manco](https://ilariamanco.com/)\*<sup>2,3</sup>,
[Emmanouil Benetos](http://www.eecs.qmul.ac.uk/~emmanouilb/)<sup>2</sup>,
[Elio Quinton](https://scholar.google.com/citations?user=IaciybgAAAAJ)<sup>3</sup>,
[George Fazekas](http://www.eecs.qmul.ac.uk/~gyorgyf/about.html)<sup>2</sup>,
[Dmitry Bogdanov](https://dbogdanov.com/)<sup>1</sup>

<sup>1</sup> UPF, <sup>2</sup>  QMUL, <sup>3</sup> UMG

</div>
* equal contribution

This repository contains code and data for the paper MuChoMusic: Evaluating Music Understanding in Multimodal Audio-Language Models (ISMIR 2024).

[TODO]

## Quick Links
- [Data](#data)
- [Datasheet](docs/datasheet.md)
- [Code Structure](#code-structure)
- [Run Evaluation](#run-evaluation)
- [Citation](#citation)
- [Contact](#contact)

## Data
The dataset is available to download from [Zenodo](https://doi.org/10.5281/zenodo.12709974):

```bash
wget -P data https://zenodo.org/record/12709974/files/muchomusic.csv
```

or via [HuggingFace Datasets](https://huggingface.co/datasets/mulab-mir/muchomusic). You can access it using the 🤗 Datasets library:

```python
from datasets import load_dataset
MuchoMusic = load_dataset("mulab-mir/muchomusic")
```

## Code setup
To use this code, we recommend creating a new python3 virtual environment:

```bash
python -m venv venv 
source venv/bin/activate
```

Then, clone the repository and install the dependencies:

```bash
git clone https://github.com/mulab-mir/muchomusic.git
cd muchomusic
pip install -r requirements.txt
```

This codebase has been tested with Python 3.11.5.

## Code Structure

```
muchomusic         
├── data            
│   └── muchomusic.csv
├── dataset_creation                # code to generate and validate the dataset
├── muchomusic_eval                 # evaluation code
│   ├── configs                     # folder to store the config files for evaluation experiments
|   └── ...    
├── evaluate.py                     # run file to run the evaluation
└── prepare_prompts.py
```

## Prepare the model outputs for benchmark

Inputs to the benchmark should be given as a JSON object with the following format:

```json
{
    "id": 415600,
    "prompt": "Question: What rhythm pattern do the digital drums follow? Options: (A) Four on the floor. (B) Off-beat syncopation. (C) Scat singing. (D) E-guitar playing a  simple melody. The correct answer is: ",
    "answers": [
        "Pop music",
        "Reggae",
        "Latin rock",
        "Ska"
    ],
    "answer_orders": [
        3,
        0,
        2,
        1
    ],
    "dataset": "sdd",
    "genre": "Reggae",
    "reasoning": [
        "genre and style"
    ],
    "knowledge": [],
    "audio_path": "data/sdd/audio/00/415600.2min.mp3",
    "model_output": "A"
}
```
To generate this, first run:

```bash
python prepare_prompts.py --output_path <path_to_json_file>
```

Then obtain the model predictions from each (audio, text) pair formed by `prompt` and the corresponding audio at `audio_path`, and populate `model_output` accordingly.

## Run the evaluation

```bash
python evaluate.py --output_dir <path_to_results_dir>
```

After running the code, the results will be stored in `<path_to_results_dir>`.

## Citation

If you use the code in this repo, please consider citing our work:

```bibtex
@inproceedings{weck2024muchomusic,
   title={MuChoMusic: Evaluating Music Understanding in Multimodal Audio-Language Models},
   author={Weck, Benno and Manco, Ilaria and Benetos, Emmanouil and Quinton, Elio and Fazekas, György and Bogdanov, Dmitry},
   booktitle = {Proceedings of the 25th International Society for Music Information Retrieval Conference (ISMIR)},
   year={2024}
}
```

## License
This repository is released under the MIT License. Please see the [LICENSE](LICENSE) file for more details. The dataset is released under the [CC BY-SA 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/).

## Contact
If you have any questions, please get in touch: [benno.weck01@estudiant.upf.edu](mailto:benno.weck01@estudiant.upf.edu), [i.manco@qmul.ac.uk](mailto:i.manco@qmul.ac.uk).

If you find a problem when using the code, you can also open an issue.
