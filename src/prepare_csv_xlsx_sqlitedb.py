from utilities.prepare_sqlitedb_from_csv_xlsx import PrepareSQLFromTabularData
from utilities.load_configiration import LoadConfiguration


con_instance = LoadConfiguration()


if __name__ == '__main__':
    prep_sql_instance = PrepareSQLFromTabularData(con_instance.directory_with_csv_xlsx)
    prep_sql_instance.run_pipeline()

    