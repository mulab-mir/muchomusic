import sys
from pathlib import Path
from typing import Type

import pandas as pd
from sqlalchemy import create_engine
from sqlmodel import select, Session, SQLModel

from interface.backend.database import Annotation, Participant, Question


def download_table(db_url, table_class: Type[SQLModel]):
    engine = create_engine(db_url, echo=True)
    with Session(engine) as session:
        results = session.exec(select(table_class)).all()
    records = [i.model_dump() for i in results]
    try:
        df = pd.DataFrame.from_records(records, index="id")
    except:
        df = pd.DataFrame.from_records(records)
    return df


if __name__ == "__main__":
    base_path = Path("../../data")
    db_url = sys.argv[1]
    tablename_mapping = {
        "annotation": Annotation,
        "participant": Participant,
        "question": Question,
    }
    for name, table in tablename_mapping.items():
        df = download_table(db_url, table)
        file_path = (base_path / name).with_suffix(".csv")
        df.to_csv(file_path)
        print(f"Wrote {file_path}")
