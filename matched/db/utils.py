from typing import Type, Literal

import pandas as pd
from pydantic import TypeAdapter
from sqlalchemy import inspect
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlmodel import SQLModel, Session, select


def read_table(session: Session, schema: Type[SQLModel], limit: int = None, offset: int = None) -> pd.DataFrame:
    """
    Read records from a table into a pandas DataFrame.

    Parameters:
    session (Session): The SQLAlchemy session to use for the query.
    schema (Type[SQLModel]): The SQLModel schema representing the table.
    limit (int, optional): The maximum number of records to retrieve. Defaults to None.
    offset (int, optional): The number of records to skip before starting to retrieve. Defaults to None.

    Returns:
    pd.DataFrame: The records from the table as a pandas DataFrame.
    """
    query = select(schema)
    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)

    results = session.exec(query).all()
    records = [record.dict() for record in results]
    df = pd.DataFrame(records)

    return df


def bulk_save_records(session: Session, df: pd.DataFrame, schema: Type[SQLModel]):
    records = df.to_dict(orient="records")
    schema_list_type = TypeAdapter(list[schema])
    instances = schema_list_type.validate_python(records)

    session.bulk_save_objects(instances)
    session.commit()


def bulk_upsert_records(
    session: Session, 
    df: pd.DataFrame, 
    schema: Type[SQLModel],
    conflict_action: Literal['update', 'nothing'] = 'nothing',
    dialect: Literal['sqlite'] = 'sqlite', 
    batch_size: int = 500
):
    # Conflict handling
    table = schema.__table__

    primary_keys = [key.name for key in inspect(table).primary_key]
    update_columns = {col.name: col for col in table.columns if col.name not in primary_keys}

    stmt_args = {'index_elements': primary_keys}
    if conflict_action == 'update':
        stmt_args['set_'] = update_columns

    # Inserting records in batches
    records = df.to_dict(orient="records")

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]

        if dialect == 'sqlite':
            stmt = sqlite_insert(table).values(batch)
        else:
            raise NotImplementedError(f'Dialect {dialect} is not supported')
    
        stmt = getattr(stmt, f'on_conflict_do_{conflict_action}')(**stmt_args)
        session.exec(stmt)
        
    session.commit()
