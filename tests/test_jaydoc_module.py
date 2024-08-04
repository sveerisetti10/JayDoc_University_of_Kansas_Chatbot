import sys
import os

# Here we add the parent directory of my_flask_app to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from my_flask_app.app import get_database, embed_message, find_similar_chunks, generate_prompt_with_context

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
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        collection = mock_db["jayhawk"]
        embedded_message = [0.1, 0.2, 0.3]
        # Here we use the find_similar_chunks function to find similar chunks
        result = find_similar_chunks(collection, embedded_message)
        collection.aggregate.assert_called_once()
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

if __name__ == "__main__":
    unittest.main()
