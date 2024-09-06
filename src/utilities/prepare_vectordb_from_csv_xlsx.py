import os
from .load_configiration import LoadConfiguration
import pandas as pd
from sentence_transformers import SentenceTransformer
from langchain_community.llms import Ollama



class PrepareVectorDBFromTabularData:
    """
    This class is designed to prepare a vector database from a CSV and XLSX file.
    It then loads the data into a ChromaDB collection. The process involves
    reading the CSV file, generating embeddings for the content, and storing 
    the data in the specified collection.
    
    Attributes:
        APPCFG: Configuration object containing settings and client instances for database and embedding generation.
        file_directory: Path to the CSV file that contains data to be uploaded.

    """

    def __init__(self, file_directory: str) -> None:
        """
        Initialize the instance with the file directory and load the app config.
        
        Args:
            file_directory (str): The directory path of the file to be processed.
        """
        self.loaded_config = LoadConfiguration()
        self.file_directory = file_directory
        self.embedding_model = SentenceTransformer(self.loaded_config.embedding_model_name)
        self.llama3 = Ollama(model="llama3")

    def run_pipeline(self):
        """
        Execute the entire pipeline for preparing the database from the CSV.
        This includes loading the data, preparing the data for injection, injecting
        the data into ChromaDB, and validating the existence of the injected data.
        """
        self.df, self.file_name = self._load_dataframe(file_directory=self.file_directory)
        self.docs, self.metadatas, self.ids, self.embeddings = self._prepare_data_for_injection(df=self.df, file_name=self.file_name)
        self._inject_data_into_chromadb()
        self._validate_db()

    def _inject_data_into_chromadb(self):
        """
        Inject the prepared data into ChromaDB.
        
        Raises an error if the collection_name already exists in ChromaDB.
        The method prints a confirmation message upon successful data injection.
        """
        collection = self.loaded_config.chroma_client.get_or_create_collection(name=self.loaded_config.collection_name)
        collection.add(
            documents=self.docs,
            metadatas=self.metadatas,
            embeddings=self.embeddings,
            ids=self.ids
        )
        print("==============================")
        print("Data is stored in ChromaDB.")
    
    def _load_dataframe(self, file_directory: str):
        """
        Load a DataFrame from the specified CSV or Excel file.
        
        Args:
            file_directory (str): The directory path of the file to be loaded.
            
        Returns:
            DataFrame, str: The loaded DataFrame and the file's base name without the extension.
            
        Raises:
            ValueError: If the file extension is neither CSV nor Excel.
        """
        # file_names_with_extensions = os.path.basename(file_directory)
        files_in_directory = [f for f in os.listdir(file_directory) if os.path.isfile(os.path.join(file_directory, f))]
        if not files_in_directory:
            raise ValueError("No files found in the directory")
        # Take the first file in the directory
        first_file = files_in_directory[0]
        print("Processing file===>", first_file)
        file_name, file_extension = os.path.splitext(first_file)
        # Construct the full file path
        full_file_path = os.path.join(file_directory, first_file)
        if file_extension == ".csv":
            df = pd.read_csv(full_file_path)
            return df, file_name
        elif file_extension == ".xlsx":
            df = pd.read_excel(full_file_path)
            return df, file_name
        else:
            raise ValueError("The selected file type is not supported")

    def _prepare_data_for_injection(self, df:pd.DataFrame, file_name:str):
        """
        Generate embeddings and prepare documents for data injection.
        
        Args:
            df (pd.DataFrame): The DataFrame containing the data to be processed.
            file_name (str): The base name of the file for use in metadata.
            
        Returns:
            list, list, list, list: Lists containing documents, metadatas, ids, and embeddings respectively.
        """
        docs = []
        metadatas = []
        ids = []
        embeddings = []
        for index, row in df.iterrows():
            output_str = ""
            # Treat each row as a separate chunk
            for col in df.columns:
                output_str += f"{col}: {row[col]},\n"
            embed = self.embedding_model.encode(output_str)
            embeddings.append(embed.tolist())
            docs.append(output_str)
            metadatas.append({"source": file_name})
            ids.append(f"id{index}")
        return docs, metadatas, ids, embeddings

    def _validate_db(self):
        """
        Validate the contents of the database to ensure that the data injection has been successful.
        Prints the number of vectors in the ChromaDB collection for confirmation.
        """
        vectordb =  self.loaded_config.chroma_client.get_collection(name=self.loaded_config.collection_name)
        print("==============================")
        print("Number of vectors in vectordb:", vectordb.count())
        print("==============================")