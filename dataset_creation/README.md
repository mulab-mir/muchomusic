# MuChoMusic Dataset Creation

This repository contains the code related to the creation of the MuChoMusic Music Question Answering Benchmark.


## Setup

### Pre-requisites
Python 3.8 or higher is required. We recommend using a virtual environment to install the dependencies.
```shell
python -m venv venv
source venv/bin/activate
```

### Installing the dependencies

```shell
pip install -r requirements.txt
```

### Downloading the data

#### SongDescriberDataset

The SongDescriberDataset can be [downloaded](https://doi.org/10.5281/zenodo.10072001) from Zenodo.

#### MusicCaps Dataset

The MusicCaps dataset can be [downloaded](https://huggingface.co/datasets/google/MusicCaps) from HuggingFace Datasets.

Additionally, the audio files need to be downloaded from YouTube. This can be done using the `download.py` script.
```shell
python musiccaps/download.py
```

### Genre tagging (optional)

For data selection genre predictions are required.
These can be generated using the `Effnet_Genres.ipynb`.

### Streamlit Questionnaire setup

Streamlit will require a path to the questionnaire data. This can be set in the `secrets.toml` file. 

```shell
cd .streamlit
cp secrets.example.toml secrets.toml
cd ..
```

Then edit the `secrets.toml` file to point to the database containing the questionnaire data. For example:

## Usage

The main steps are:
1. Selecting the captions from the respective datasets.
2. Generating the question data.
3. Running the questionnaire for annotation.
4. Building the benchmark from the annotated data.

The questionnaire is built using Streamlit.

### Preparing the questionnaire data

1. [`caption_selection.ipynb`](caption_selection.ipynb) - This notebook will select the captions from the respective datasets.
2. The question data is generated using the [`generate_gemini.ipynb`](generate_gemini.ipynb) notebook.
This notebook will generate markdown files
containing the full model output including the questions/answers.

### Running Streamlit Questionnaire

To run the questionnaire, use the following command:
```shell
streamlit run interface/welcome.py
```

### Building benchmark after annotation

[`build_benchmark.ipynb`](build_benchmark.ipynb) - This notebook will build the benchmark from the annotated data.
