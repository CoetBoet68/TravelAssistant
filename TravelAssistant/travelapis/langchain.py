import environ
from langchain.agents import AgentType
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_community.llms import OpenAI
from langchain_community.utilities import SQLDatabase
import ast

class langchainAPI():
    agent_executor = None

    def __init__(self):
        env = environ.Env()
        environ.Env.read_env()
        user = env('AWS_DB_USER')
        password = env('AWS_DB_PASSWORD')
        host = env('AWS_DB_ENDPOINT')
        port = '7070'
        open_key = env('OPENAI_API_KEY')
        self.pg_uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/assistant"
        db = SQLDatabase.from_uri(self.pg_uri)
        llm =  OpenAI()
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        self.agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        )

    def get_response(self, question):
        response = self.agent_executor.run(f"Respond with Top 10 location ids in format ['id1','id2','id3']"
                                           f" for following user prompt (try to get most suitable location querying the various columns): {question}")
        print(response)
        try:
            if not response[-1] == ']':
                last_quote_index = response.rfind(",")
                trimmed_string = response[:last_quote_index] + ']'
                print(trimmed_string)
                ids = ast.literal_eval(trimmed_string)
            else:
                ids = ast.literal_eval(response)
            return ids
        except:
            return "Not Correct Format"

