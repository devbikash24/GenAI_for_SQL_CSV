import os
from dotenv import load_dotenv
import yaml
from pathlib import Path
import logging
import chromadb
from langchain_community.llms import Ollama


logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s')

if load_dotenv():
    logging.info("Environment Variable Loaded Successfully")


def find_project_root(indicator: str = "configuration") -> Path:
    """
    Find the project root directory by searching for a specific indicator directory or file.
    
    Args:
        indicator (str): The directory or file to look for that signifies the project root.
        
    Returns:
        Path: The Path object pointing to the project root.
    """
    current_dir = Path(__file__).resolve().parent
    
    while not (current_dir / indicator).exists():
        if current_dir.parent == current_dir:
            raise FileNotFoundError(f"Cannot find project root containing '{indicator}'")
        current_dir = current_dir.parent
    
    return current_dir


class LoadConfiguration:

    def __init__(self) -> None:
        self.project_root = find_project_root()
        config_file = self.project_root / "configuration" / "config.yaml"
        with config_file.open() as f:
            app_config = yaml.load(f, Loader=yaml.SafeLoader)

        self.load_directories(app_config=app_config)

        self.load_llm_configs(app_config=app_config)
        # self.load_openai_models()
        self.load_opensource_model()
        self.load_chroma_client()
        self.load_rag_config(app_config=app_config) 

        # Un comment the code below if you want to clean up the upload csv SQL DB on every fresh run of the chatbot. (if it exists)
        # self.remove_directory(self.uploaded_files_sqldb_directory)

    def load_directories(self, app_config):

        self.directory_with_csv_xlsx = self.project_root / app_config['directories']['directory_with_csv_xlsx']
        self.sqlbd_directory = self.project_root / app_config['directories']['sqldb_directory']
        self.uploaded_files_sqldb_directory = self.project_root / app_config['directories']['directory_for_uploaded_sqldb']
        self.stored_csv_xlsx_sqldb_directory = self.project_root / app_config["directories"]["stored_csv_xlsx_sqldb_directory"]
        self.persist_directory = self.project_root / app_config["directories"]["persist_directory"]

    def load_llm_configs(self, app_config):
        self.model_name = app_config["llm_config"]["model_name"]
        self.agent_llm_system_role = app_config["llm_config"]["agent_llm_system_role"]
        self.rag_llm_system_role = app_config["llm_config"]["rag_llm_system_role"]
        self.temperature = app_config["llm_config"]["temperature"]
        self.embedding_model_name = app_config["llm_config"]["embedding_model_name"]

    def load_opensource_model(self):
        pass
        # Use Llama3 model from Ollama via langchain_community.llms
        # self.llama3_model = Ollama(base_url=os.getenv("OPENAI_API_BASE"),model=self.model_name)

    def load_chroma_client(self):
        self.chroma_client = chromadb.PersistentClient(path=str(self.persist_directory))

    def load_rag_config(self, app_config):
        self.collection_name = app_config["rag_config"]["collection_name"]
        self.top_k = app_config["rag_config"]["top_k"]

    def remove_directory(self, directory_path: Path):
        """
            Removes the specified directory and its contents.

            Parameters:
                directory_path (Path): The path of the directory to be removed.

            Raises:
                OSError: If an error occurs during the directory removal process.

            Returns:
                None
        """
        if directory_path.exists() and directory_path.is_dir():
            for item in directory_path.iterdir():
                if item.is_dir():
                    self.remove_directory(item)  # Recursively remove subdirectories
                else:
                    item.unlink()  # Remove files
            directory_path.rmdir()  # Finally, remove the directory itself
            print(f"The directory '{directory_path}' has been successfully removed.")
        else:
            print(f"The directory '{directory_path}' does not exist.")



