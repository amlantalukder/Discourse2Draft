from pathlib import Path
import pandas as pd

def selectFromDB(table_name: str, field_names: list, field_values: list[list]):
    
    path_credential_table = Path(f'data/{table_name}.csv')
    table = pd.read_csv(path_credential_table, keep_default_na=False)

    records = []
    for i, row in table.iterrows():
        for f, v in list(zip(field_names, field_values)):
            if row[f] not in v:
                break
        else:
            records.append(row)

    return pd.DataFrame(records)


def insertIntoDB(table_name: str, field_names: list, field_values: list):

    path_credential_table = Path(f'data/{table_name}.csv')
    table = pd.read_csv(path_credential_table, keep_default_na=False)
    
    d = dict(zip(field_names, field_values))

    table = pd.concat([table, pd.DataFrame(d)])
    table.to_csv(path_credential_table, index=None)

def updateDB(table_name: str, update_fields: list, update_values: list, select_fields: list, select_values: list[list]):

    path_credential_table = Path(f'data/{table_name}.csv')
    table = pd.read_csv(path_credential_table, keep_default_na=False)
    
    for i, row in table.iterrows():
        for f_s, v_s in list(zip(select_fields, select_values)):
            if row[f_s] not in v_s:
                break
        else:
            for u_f, u_v in list(zip(update_fields, update_values)):
                table.loc[row.name, u_f] = u_v

    table.to_csv(path_credential_table, index=None)