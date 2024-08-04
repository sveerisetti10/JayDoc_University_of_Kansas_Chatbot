import certifi
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import re
import time

app = Flask(__name__)
CORS(app)

def get_database():
    """
    Purpose: Connect to the MongoDB database and return the database object.
    """
    uri = "mongodb+srv://sriveerisetti:jayhawk@jayhawk.srjqsho.mongodb.net/?retryWrites=true&w=majority&appName=Jayhawk"
    ca = certifi.where()
    client = MongoClient(uri, tlsCAFile=ca)
    # This is the name of the database that we will be using
    db = client["JayDoc"]
    return db

def embed_message(user_message):
    """
    Purpose: Embed the user's message using the GIST-large model.
    Input: user_message - The message that the user has entered.
    """
    # GIST is one of the best models for sentence embeddings
    model = SentenceTransformer("avsolatorio/GIST-large-Embedding-v0")
    query_embedding = model.encode([user_message], convert_to_tensor=True).tolist()[0]
    return query_embedding

def find_similar_chunks(collection, embedded_message, index_name="jayhawk", max_results=3):
    """
    Purpose: Find similar chunks in the MongoDB collection based on the user's embedded message.
    Input: collection - The MongoDB collection where the chunks are stored.
    Input: embedded_message - The embedded message that the user has entered.
    Input: index_name - The name of the index to use for searching.
    Input: max_results - The maximum number of results to return.
    """
    query = [
        {
            "$vectorSearch": {
                "index": index_name,
                "path": "embedding",
                "queryVector": embedded_message,
                "numCandidates": 20,
                "limit": max_results,
            }
        }
    ]
    results = list(collection.aggregate(query))
    chunks = []
    for result in results:
        chunk = result.get("chunk", "N/A")
        similarity = result.get("similarity", "N/A")
        source = result.get("source", "N/A")
        # We store the chunk, similarity, and source in a tuple
        chunks.append((chunk, similarity, source))
    return chunks

def generate_prompt_with_context(relevant_chunks, query):
    """
    Purpose: Generate a prompt with the relevant context for the Mistral model.
    Input: relevant_chunks - A list of relevant chunks from the database.
    Input: query - The user's query.
    """
    context = "Based on the following information: "
    for chunk, similarity, source in relevant_chunks:
        context += f"\n- [Source: {source}]: {chunk}"
    # Here we create a comprehensive prompt that includes the context and the user's query
    prompt = f"{context}\n\n{query}"
    return prompt

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def generate_text_with_mistral(prompt, temperature=0.7):
    """
    Purpose: Generate text using the Mistral model based on the prompt and temperature.
    Input: prompt - The prompt for the Mistral model.
    """
    # We define the LLAMAFILE_PATH environment variable in docker-compose.yml
    llamafile_path = os.getenv('LLAMAFILE_PATH')
    if not llamafile_path:
        raise ValueError("LLAMAFILE_PATH environment variable is not set")

    print(f"Using llamafile_path: {llamafile_path}")
    escaped_prompt = prompt.replace("'", "'\\''")
    # Here we run a command line command to generate text using the Mistral model
    command = f"{llamafile_path} --temp {temperature} -p '[INST]{escaped_prompt}[/INST]'"
    print(f"Running command: {command}")
    # Here we store the result of the command in the result variable
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    # Debugging information
    if result.returncode != 0:
        print(f"Error during text generation: {result.stderr}")
        return None
    # Here we extract the generated text from the result
    generated_text = result.stdout.strip()
    # We do not want the relevant context to be part of the response
    cleaned_text = generated_text.replace("<s>", "").replace("</s>", "").strip()
    # We remove the [INST] and [/INST] tags from the response
    response = re.sub(r"\[INST\].*?\[/INST\]", "", cleaned_text, flags=re.DOTALL).strip()
    # We return the generated response
    return response

# Here we define the route for the /query endpoint. We expect a POST request with JSON data.
@app.route("/query", methods=["POST"])
def query():
    # We start a timer to measure the processing time
    start_time = time.time()
    print("Received POST request at /query")
    # We extract the JSON data from the request
    data = request.json
    print(f"Request data: {data}")
    # We extract the user's query and the temperature from the JSON data
    user_query = data.get("query")
    temperature = data.get("temperature", 0.7)
    print(f"Query: {user_query}, Temperature: {temperature}")
    # If the user has provided a query, we proceed with generating a response
    if user_query:
        # This times the database connection
        db_start_time = time.time()
        # Here we use get_database to connect to the MongoDB database
        db = get_database()
        collection = db["jayhawk"]
        db_end_time = time.time()
        print(f"Database connection time: {db_end_time - db_start_time:.2f} seconds")

        # This times the embedding process
        embed_start_time = time.time()
        # Here we use the embed_message function to embed the user's message
        embedded_query = embed_message(user_query)
        embed_end_time = time.time()
        print(f"Embedding time: {embed_end_time - embed_start_time:.2f} seconds")

        # Here we time the database query
        query_start_time = time.time()
        # Here we use find_similar_chunks to find relevant chunks in the database
        relevant_chunks = find_similar_chunks(collection, embedded_query)
        query_end_time = time.time()
        print(f"Database query time: {query_end_time - query_start_time:.2f} seconds")

        # Here we see how long it takes to generate the prompt
        prompt_start_time = time.time()
        if relevant_chunks:
            # Here we use the 
            prompt = generate_prompt_with_context(relevant_chunks, user_query)
        else:
            prompt = user_query
        prompt_end_time = time.time()
        print(f"Prompt generation time: {prompt_end_time - prompt_start_time:.2f} seconds")

        # Here we time the text generation process
        response_start_time = time.time()
        # Here we use the generate_text_with_mistral function to generate a response
        response = generate_text_with_mistral(prompt, temperature)
        response_end_time = time.time()
        print(f"Text generation time: {response_end_time - response_start_time:.2f} seconds")

        end_time = time.time()
        print(f"Total processing time: {end_time - start_time:.2f} seconds")

        # Here we add some debugging information to the response
        if response:
            return jsonify({"response": response})
        else:
            return jsonify({"error": "Error generating response"}), 500
    else:
        return jsonify({"error": "No query provided"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
