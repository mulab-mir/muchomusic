import json
from pathlib import Path
from typing import Optional, List, Tuple

import streamlit as st
from sqlalchemy import func, not_
from sqlmodel import Field, Session, SQLModel, create_engine, Relationship, select


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dataset: str
    dataset_identifier: str
    question: str
    correct_answer: str
    distractor_1: str
    distractor_2: str
    distractor_3: str

    annotations: List["Annotation"] = Relationship(back_populates="question")


class Annotation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: Optional[int] = Field(default=None, foreign_key="question.id")
    participant_id: str = Field(foreign_key="participant.id")
    answer: Optional[str]
    time: Optional[float]
    unfinished: bool
    question: Optional[Question] = Relationship(back_populates="annotations")


class Participant(SQLModel, table=True):
    id: str = Field(primary_key=True)
    study_id: Optional[str] = None
    fluent_in_english: bool
    no_hearing_loss: bool
    no_language_disorders: bool
    musician: bool
    passed_comprehension_check: bool = False
    completion_code: Optional[str] = None


def _get_unfinished_annotation(
    engine, participant_id: str
) -> Optional[Tuple[Question, int]]:
    with Session(engine) as session:
        statement = (
            select(Question, Annotation.id)
            .join(Annotation)
            .where(
                Annotation.participant_id == participant_id,
                Annotation.unfinished,
            )
        )
        results = session.exec(statement)
        return results.one_or_none()


def _get_unlabelled_question(session) -> Optional[Question]:
    statement = (
        select(Question)
        .order_by(func.random())
        .join(Annotation, isouter=True)
        .where(Annotation.id == None)
        .limit(1)
    )
    results = session.exec(statement)
    return results.one_or_none()


def _get_min_labelled_question(session, participant_id) -> Question:
    already_seen = select(Annotation.question_id).where(
        Annotation.participant_id == participant_id
    )
    statement = (
        select(func.count(Annotation.id).label("annotations_count"))
        .where(not_(Annotation.question_id.in_(already_seen)))
        .group_by(Annotation.question_id)
        .order_by("annotations_count")
        .limit(1)
    )
    count_result = session.exec(statement)
    annotation_count = count_result.one()
    statement = (
        select(Question)
        .order_by(func.random())
        .limit(1)
        .join(Annotation)
        .where(not_(Annotation.question_id.in_(already_seen)))
        .group_by(Question.id)
        .having(func.count(Annotation.id) == annotation_count)
    )
    results = session.exec(statement)
    question = results.one()
    return question


def _get_new_annotation_item(engine, participant_id):
    with Session(engine) as session:
        question = _get_unlabelled_question(session)
        if question is None:
            question = _get_min_labelled_question(session, participant_id)
        # add an uncompleted annotation
        annotation = Annotation(participant_id=participant_id, unfinished=True)
        session.add(annotation)
        question.annotations.append(annotation)
        session.commit()
        annotation_id = annotation.id
        session.refresh(question)
    return question, annotation_id


def get_item_for_annotation(database_url, participant_id: str) -> Tuple[Question, int]:
    engine = connect(database_url)
    unfinished = _get_unfinished_annotation(engine, participant_id)
    if unfinished is not None:
        return unfinished
    return _get_new_annotation_item(engine, participant_id)


def add_annotation(database_url, annotation_id: int, answer: str, time: float):
    engine = connect(database_url)
    with Session(engine) as session:
        annotation = session.exec(
            select(Annotation).where(Annotation.id == annotation_id)
        ).one()
        annotation.answer = answer
        annotation.time = time
        annotation.unfinished = False
        session.add(annotation)
        session.commit()


def num_annotations_for_participant(database_url, participant_id: str) -> int:
    engine = connect(database_url)
    with Session(engine) as session:
        statement = select(func.count(Annotation.id)).where(
            Annotation.participant_id == participant_id,
            not_(Annotation.unfinished),
        )
        results = session.exec(statement)
        return results.one()


def add_participant(
    database_url,
    participant_id: str,
    study_id: Optional[str],
    fluent_in_english: bool,
    no_hearing_loss: bool,
    no_language_disorders: bool,
    musician: bool,
):
    engine = connect(database_url)
    with Session(engine) as session:
        participant = Participant(
            id=participant_id,
            study_id=study_id,
            fluent_in_english=fluent_in_english,
            no_hearing_loss=no_hearing_loss,
            no_language_disorders=no_language_disorders,
            musician=musician,
        )
        session.add(participant)
        session.commit()


def get_participant(database_url, participant_id: str) -> Optional[Participant]:
    engine = connect(database_url)
    with Session(engine) as session:
        statement = select(Participant).where(Participant.id == participant_id)
        results = session.exec(statement)
        return results.one_or_none()


def participant_passed_comprehension_check(database_url, participant_id: str):
    engine = connect(database_url)
    with Session(engine) as session:
        participant = session.exec(
            select(Participant).where(Participant.id == participant_id)
        ).one()
        participant.passed_comprehension_check = True
        session.add(participant)
        session.commit()


def add_completion_code(database_url, participant_id: str, completion_code: str):
    engine = connect(database_url)
    with Session(engine) as session:
        participant = session.exec(
            select(Participant).where(Participant.id == participant_id)
        ).one()
        participant.completion_code = completion_code
        session.add(participant)
        session.commit()


def _build_question_object(
    dataset: str, identifier: str, question: str, answer: str, distractors
) -> Question:
    return Question(
        dataset=dataset,
        dataset_identifier=identifier,
        question=question,
        correct_answer=answer,
        distractor_1=distractors["incorrect_but_related"]["distractor"],
        distractor_2=distractors["correct_but_unrelated"]["distractor"],
        distractor_3=distractors["incorrect_and_unrelated"]["distractor"],
    )


def _question_reader(identifier, sdd_data, dataset="sdd"):
    for question in sdd_data["questions"]:
        distractors = question["distractors"]
        yield _build_question_object(
            dataset,
            identifier,
            question["question"],
            question["correct_answer"],
            distractors,
        )


def add_questions(db_url, questions_dir, dataset):
    engine = connect(db_url, verbose=True)
    for questions_file in Path(questions_dir).glob("*.json"):
        with open(questions_file, "r") as f:
            question_data = json.load(f)
        question_gen = _question_reader(questions_file.stem, question_data, dataset)
        with Session(engine) as session:
            for question in question_gen:
                session.add(question)
            session.commit()


@st.cache_resource(max_entries=1)
def connect(db_url, verbose=False):
    engine = create_engine(db_url, echo=verbose)
    return engine


def create_db_and_tables(db_url):
    engine = create_engine(db_url, echo=True)
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    # hint: create the database file first
    # sqlite3 data/music_question_answering.db "VACUUM;"
    base_path = "./"
    db_url = f"sqlite:///{base_path}data/music_question_answering.db"
    create_db_and_tables(db_url)
    # add_questions(db_url, f"{base_path}musiccaps/musiccaps_questions.json", "musiccaps")
    # add_questions(db_url, f"{base_path}SongDescriberDataset/sdd_questions.json", "sdd")
