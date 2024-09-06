import os
from typing import List, Tuple
from utilities.load_configiration import LoadConfiguration
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent
import langchain
from langchain_community.llms import Ollama
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import AgentType
from sentence_transformers import SentenceTransformer



langchain.debug = True

loading_configuration = LoadConfiguration()

class ChatBot:
    """
    A ChatBot class capable of responding to messages using different modes of operation.
    It can interact with SQL databases, leverage language chain agents for Q&A,
    and use embeddings for Retrieval-Augmented Generation (RAG) with ChromaDB.
    """
    client = Ollama(base_url='http://localhost:11434', model='llama3', temperature=0.0)
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    @staticmethod
    def respond(chatbot: List, message: str, chat_type: str, app_functionality: str) -> Tuple:
        """
        Respond to a message based on the given chat and application functionality types.

        Args:
            chatbot (List): A list representing the chatbot's conversation history.
            message (str): The user's input message to the chatbot.
            chat_type (str): Describes the type of the chat (interaction with SQL DB or RAG).
            app_functionality (str): Identifies the functionality for which the chatbot is being used (e.g., 'Chat').

        Returns:
            Tuple[str, List, Optional[Any]]: A tuple containing an empty string, the updated chatbot conversation list,
                                             and an optional 'None' value. The empty string and 'None' are placeholder
                                             values to match the required return type and may be updated for further functionality.
                                             Currently, the function primarily updates the chatbot conversation list.
        """
        if app_functionality == "Chat":
            # If we want to use langchain agents for Q&A with our SQL DBs that was created from .sql files.
            if chat_type == "Q&A with stored SQL-DB":
                # directories
                if os.path.exists(loading_configuration.sqlbd_directory):
                    db = SQLDatabase.from_uri(
                        f"sqlite:///{loading_configuration.sqlbd_directory}")
                    agent_executor = create_sql_agent(ChatBot.client, db=db, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose = True)
                    response = agent_executor.invoke(message)
                    response = response["output"]

                else:
                    # chatbot.append(
                    #     {"input":message, "bot":f"SQL DB does not exist. Please first create the 'sqldb.db'."})
                    return message, "SQL DB does not exist. Please first create the 'sqldb.db'."
            # If we want to use langchain agents for Q&A with our SQL DBs that were created from CSV/XLSX files.
            elif chat_type == "Q&A with Uploaded CSV/XLSX SQL-DB" or chat_type == "Q&A with stored CSV/XLSX SQL-DB":
                if chat_type == "Q&A with Uploaded CSV/XLSX SQL-DB":
                    if os.path.exists(loading_configuration.uploaded_files_sqldb_directory):
                        engine = create_engine(
                            f"sqlite:///{loading_configuration.uploaded_files_sqldb_directory}")
                        db = SQLDatabase(engine=engine)
                        print(db.dialect)
                    else:
                        # chatbot.append(
                            # {"input":message, "bot":f"SQL DB from the uploaded csv/xlsx files does not exist. Please first upload the csv files from the chatbot."})
                        return message, "SQL DB from the uploaded csv/xlsx files does not exist. Please first upload the csv files from the chatbot."
                elif chat_type == "Q&A with stored CSV/XLSX SQL-DB":
                    if os.path.exists(loading_configuration.stored_csv_xlsx_sqldb_directory):
                        engine = create_engine(
                            f"sqlite:///{loading_configuration.stored_csv_xlsx_sqldb_directory}")
                        db = SQLDatabase(engine=engine)
                    else:
                        # chatbot.append(
                            # {"input":message, "bot":f"SQL DB from the stored csv/xlsx files does not exist. Please first execute `src/prepare_csv_xlsx_sqlitedb.py` module."})
                        return message, "SQL DB from the stored csv/xlsx files does not exist. Please first execute `src/prepare_csv_xlsx_sqlitedb.py` module."
               
                agent_executor = create_sql_agent(ChatBot.client, db=db, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose = True)
                response = agent_executor.invoke(message)
                response = response["output"]

            elif chat_type == "RAG with stored CSV/XLSX ChromaDB":
                query_embeddings = ChatBot.embedding_model.encode(message)
                vectordb = loading_configuration.chroma_client.get_collection(
                    name=loading_configuration.collection_name)
                results = vectordb.query(
                    query_embeddings=query_embeddings.tolist(),
                    n_results=loading_configuration.top_k
                )
                prompt = f"User's question: {message} \n\n Search results:\n {results}"

                messages = [
                    {"role": "system", "content": str(
                        loading_configuration.rag_llm_system_role
                    )},
                    {"role": "user", "content": prompt}
                ]
                response = ChatBot.client.invoke(messages)
                # response = llm_response.choices[0].message.content

            # Get the `response` variable from any of the selected scenarios and pass it to the user.
            chatbot.append(
                {"input":message,"bot": response})
            return message, response
        else:
            pass