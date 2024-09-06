import os
import logging
import pandas as pd
from sqlalchemy import create_engine, inspect
from .load_configiration import LoadConfiguration

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s')


class PrepareSQLFromTabularData:
    """
    Prepare SQL statements from tabular data.
    """

    def __init__(self, file_dir) -> None:
        """
        Initialize an instance of PrepareSQLFromTabularData.

        Args:
            files_dir (str): The directory containing the CSV or XLSX files to be converted to SQL tables.
        """

        loaded_config = LoadConfiguration()
        self.files_directory = file_dir
        self.file_dir_list = os.listdir(file_dir)
        db_path = loaded_config.stored_csv_xlsx_sqldb_directory
        db_path = f"sqlite:///{db_path}"
        self.engine = create_engine(db_path)
        logging.info("Number of csv files: %d", len(self.file_dir_list))

    def _prepare_db(self):
        """
        Private method to convert CSV/XLSX files from the specified directory into SQL tables.

        Each file's name (excluding the extension) is used as the table name.
        The data is saved into the SQLite database referenced by the engine attribute.
        """
        for file in self.file_dir_list:
            full_file_path = os.path.join(self.files_directory, file)
            file_name, file_extension = os.path.splitext(file)
            if file_extension == ".csv":
                df = pd.read_csv(full_file_path)
            elif file_extension == ".xlsx":
                df = pd.read_excel(full_file_path)
            else:
                raise ValueError("The selected file type is not supported")
            df.to_sql(file_name, self.engine, index=False)
        logging.info("All csv files are saved into the sql database.")

    def _validate_db(self):
        """
        Private method to validate the tables stored in the SQL database.

        It prints out all available table names in the created SQLite database
        to confirm that the tables have been successfully created.
        """
        insp = inspect(self.engine)
        table_names = insp.get_table_names()
        logging.info("Available table names in created SQL DB: %s", table_names)


    def run_pipeline(self):
        """
        Public method to run the data import pipeline, which includes preparing the database
        and validating the created tables. It is the main entry point for converting files
        to SQL tables and confirming their creation.
        """
        self._prepare_db()
        self._validate_db()


        






