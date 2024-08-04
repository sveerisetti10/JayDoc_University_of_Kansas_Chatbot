import sys
import os

# Here we add the parent directory of my_flask_app to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from my_flask_app.app import get_database, embed_message, find_similar_chunks, generate_prompt_with_context, generate_text_with_mistral, app

class TestDatabaseConnection(unittest.TestCase):
    @patch("my_flask_app.app.MongoClient")
    @patch("my_flask_app.app.certifi.where")
    def test_get_database(self, mock_certifi, mock_mongo_client):
        """
        Purpose: Test the get_database function to ensure that it connects to the MongoDB database correctly.
        Input: mock_certifi - MagicMock object for the certifi.where function
        Input: mock_mongo_client - MagicMock object for the MongoClient class
        Output: Assert that the MongoClient is called with the correct parameters and the database is returned.
        """
        mock_certifi.return_value = "path/to/cert"
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        # Here we use the get_database function to connect to the MongoDB database
        db = get_database()
        mock_mongo_client.assert_called_with(
            "mongodb+srv://sriveerisetti:jayhawk@jayhawk.srjqsho.mongodb.net/?retryWrites=true&w=majority&appName=Jayhawk",
            tlsCAFile="path/to/cert",
        )
        # The database is called JayDoc
        self.assertEqual(db, mock_client["JayDoc"])

class TestEmbedMessage(unittest.TestCase):
    @patch("my_flask_app.app.SentenceTransformer")
    def test_embed_message(self, mock_sentence_transformer):
        """
        Purpose: Test the embed_message function to ensure that it embeds the user's message correctly.
        Input: mock_sentence_transformer - MagicMock object for the SentenceTransformer class
        Output: Assert that the model is called with the correct parameters and the embedded message is returned.
        """
        mock_model = MagicMock()
        mock_sentence_transformer.return_value = mock_model
        mock_model.encode.return_value = MagicMock()
        # Here we predetermine the output of the model.encode function
        mock_model.encode.return_value.tolist.return_value = [[0.1, 0.2, 0.3]]
        # Here we use the embed_message function to embed the user's message
        result = embed_message("Test message")
        self.assertEqual(result, [0.1, 0.2, 0.3])

class TestFindSimilarChunks(unittest.TestCase):
    @patch("my_flask_app.app.get_database")
    def test_find_similar_chunks(self, mock_get_db):
        """
        Purpose: Test the find_similar_chunks function to ensure that it retrieves similar chunks from the database.
        Input: mock_get_db - MagicMock object for the get_database function
        Output: Assert that the collection is queried and the results are returned as a list
        """
        # Here the mock_db object simulates the MongoDB database
        mock_db = MagicMock()
        # Here we configure the mock object to return the collection
        mock_get_db.return_value = mock_db
        collection = mock_db["jayhawk"]
        embedded_message = [0.1, 0.2, 0.3]
        # Here we define some mock chunks that will be returned by mock collection.aggregate
        expected_chunks = [
            {"chunk": "chunk1", "similarity": 0.9, "source": "source1"},
            {"chunk": "chunk2", "similarity": 0.8, "source": "source2"},
            {"chunk": "chunk3", "similarity": 0.7, "source": "source3"},
        ]
        collection.aggregate.return_value = expected_chunks
        # Here we use the find_similar_chunks function to find similar chunks
        result = find_similar_chunks(collection, embedded_message)
        collection.aggregate.assert_called_once()
        # Here we are making sure that the function returns a list of chunks
        self.assertIsInstance(result, list)

class TestGeneratePromptWithContext(unittest.TestCase):
    def test_generate_prompt_with_context(self):
        """
        Purpose: Test the generate_prompt_with_context function to ensure that it generates the prompt correctly.
        Output: Assert that the prompt contains the relevant chunks and the user's query.
        """
        relevant_chunks = [("chunk1", 0.9, "source1")]
        query = "Test query"
        # Here we use the generate_prompt_with_context function to generate a prompt
        prompt = generate_prompt_with_context(relevant_chunks, query)
        self.assertIn("Based on the following information", prompt)
        self.assertIn("[Source: source1]: chunk1", prompt)
        self.assertIn(query, prompt)

class TestGenerateTextWithMistral(unittest.TestCase):
    @patch("my_flask_app.app.subprocess.run")
    @patch.dict(os.environ, {"LLAMAFILE_PATH": "/path/to/llamafile"})
    def test_generate_text_with_mistral(self, mock_subprocess_run):
        """
        Purpose: Test the generate_text_with_mistral function to ensure that it correctly generates text using the Mistral model.
        Input: mock_subprocess_run - MagicMock object for the subprocess.run function.
        Output: Assert that the function returns the expected response text.
        """
        # The mock_resturn object simulates the output of the subprocess.run function
        mock_result = MagicMock()
        mock_result.returncode = 0
        # Here we want to test to see if the function will handle the output correctly by stripping the tags
        mock_result.stdout.strip.return_value = "<s>Generated text</s>"
        mock_subprocess_run.return_value = mock_result

        prompt = "Test prompt"
        temperature = 0.7
        # Here we want to test the generate_text_with_mistral function
        result = generate_text_with_mistral(prompt, temperature)

        # Here we want to check if the subprocess.run function was called with the correct parameters
        expected_command = f"{os.getenv('LLAMAFILE_PATH')} --temp {temperature} -p '[INST]{prompt}[/INST]'"
        mock_subprocess_run.assert_called_once_with(expected_command, shell=True, capture_output=True, text=True)

        # Here we want to check if the function returns the expected generated
        self.assertEqual(result, "Generated text")

class TestQueryEndpoint(unittest.TestCase):
    @patch("my_flask_app.app.get_database")
    @patch("my_flask_app.app.embed_message")
    @patch("my_flask_app.app.find_similar_chunks")
    @patch("my_flask_app.app.generate_text_with_mistral")
    def test_query_endpoint(self, mock_generate_text, mock_find_chunks, mock_embed, mock_get_db):
        """
        Purpose: Test the /query endpoint to ensure that it returns a valid response.
        Input: mock_generate_text - MagicMock object for the generate_text_with_mistral function
        Input: mock_find_chunks - MagicMock object for the find_similar_chunks function
        Input: mock_embed - MagicMock object for the embed_message function
        Input: mock_get_db - MagicMock object for the get_database function
        Output: Assert that the response contains the generated text.
        """
        # The mock objects simulate the output of the functions
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_embed.return_value = [0.1, 0.2, 0.3]
        mock_find_chunks.return_value = [("chunk1", 0.9, "source1")]
        mock_generate_text.return_value = "Generated response"

        tester = app.test_client(self)
        # Here we are testing if the POST request to the /query endpoint returns a valid response
        response = tester.post('/query', json={"query": "Test query", "temperature": 0.7})

        # Here we want to check if the response contains the generated text
        self.assertEqual(response.status_code, 200)
        # Here we check if the JSON object contains the generated response "Generated response"
        self.assertIn("Generated response", response.get_json()["response"])

if __name__ == "__main__":
    unittest.main()
