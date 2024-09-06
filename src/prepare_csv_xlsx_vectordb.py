from utilities.prepare_vectordb_from_csv_xlsx import PrepareVectorDBFromTabularData
from pathlib import Path

if __name__ == '__main__':
    titanic_dir = Path("D:/Generative AI/generative ai project/QA_SQL_Tabular_data/data/for_uploads")
    data_prep_instance = PrepareVectorDBFromTabularData(file_directory=titanic_dir)
    data_prep_instance.run_pipeline()

    