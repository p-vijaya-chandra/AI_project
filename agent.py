from dotenv import load_dotenv
import os

# LangChain and related imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from github import fetch_github_issues  # Custom function to fetch GitHub issues
from note import note_tool  # Custom tool for managing notes

# Load environment variables from a .env file
load_dotenv()

# Function to initialize and connect to the AstraDB Vector Store
def initialize_vectorstore():
    """
    Establishes a connection to the AstraDB vector store using API endpoint,
    token, and namespace from environment variables. Embeddings are provided
    via OpenAIEmbeddings.
    """
    # Initialize embeddings for storing and searching documents
    openai_embeddings = OpenAIEmbeddings()

    # Load API credentials and keyspace (namespace) from environment variables
    astra_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
    astra_app_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    astra_namespace = os.getenv("ASTRA_DB_KEYSPACE")

    # Set namespace, defaulting to None if not provided
    if astra_namespace:
        astra_keyspace = astra_namespace
    else:
        astra_keyspace = None

    # Create and return a connection to the AstraDB vector store
    vectorstore = AstraDBVectorStore(
        embedding=openai_embeddings,
        collection_name="github",  # Name of the collection in the DB
        api_endpoint=astra_api_endpoint,
        token=astra_app_token,
        namespace=astra_keyspace,
    )
    return vectorstore


# Initialize the vector store connection
vector_store = initialize_vectorstore()

# Ask user if they want to fetch and update GitHub issues in the vector store
update_issues_flag = input("Do you want to update the issues? (y/N): ").lower() in [
    "yes",
    "y",
]

if update_issues_flag:
    """
    Fetch GitHub issues, delete the current vector store collection (if exists),
    and add the fetched issues to the vector store.
    """
    github_owner = "techwithtim"  # GitHub repository owner
    github_repo = "Flask-Web-App-Tutorial"  # GitHub repository name

    # Fetch GitHub issues
    fetched_issues = fetch_github_issues(github_owner, github_repo)

    try:
        # Delete existing collection in the vector store
        vector_store.delete_collection()
    except:
        pass  # Ignore errors if collection does not exist

    # Re-initialize the vector store and add the fetched issues
    vector_store = initialize_vectorstore()
    vector_store.add_documents(fetched_issues)

# Create a retriever tool for querying the vector store
retriever_instance = vector_store.as_retriever(search_kwargs={"k": 3})
retriever_tool = create_retriever_tool(
    retriever_instance,
    "github_search",
    "Search for information about GitHub issues. For any questions about GitHub issues, you must use this tool!",
)

# Pull a predefined prompt template from the LangChain hub
prompt_template = hub.pull("hwchase17/openai-functions-agent")

# Initialize the language model
language_model = ChatOpenAI()

# Define tools available to the agent
tools_list = [retriever_tool, note_tool]

# Create an agent for tool calling
agent_instance = create_tool_calling_agent(language_model, tools_list, prompt_template)

# Create an agent executor to handle user queries
agent_executor = AgentExecutor(agent=agent_instance, tools=tools_list, verbose=True)

# Main loop to interact with the user
while (user_question := input("Ask a question about GitHub issues (q to quit): ")) != "q":
    """
    Continuously take user input (questions about GitHub issues) and invoke the
    agent executor to process the input and provide answers.
    """
    response = agent_executor.invoke({"input": user_question})
    print(response["output"])
