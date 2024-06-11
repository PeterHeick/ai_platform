import unittest
import os
import json
import time
import sys
from dotenv import load_dotenv


# Tilføj src/db-mappen til sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'services')))

from chatbot_service import queryRetriever

load_dotenv()

class TestChromaDBClient(unittest.TestCase):

    def test_query_retriever(self):
        # Test retriever funktionalitet
        print("Test retriever funktionalitet")
        retriever_chain = queryRetriever()
        
        session_id = "test_session"  
        # Simuler en forespørgsel
        input_data = {
            "chat_history": [],
            "input": "What are the GDPR rules?"
        }
        # result = retriever_chain.invoke(input_data)
        result = retriever_chain.invoke(input_data, config={"configurable": {"session_id": session_id}})  
        print(result['answer'])

        for doc in result['context']:
            print(doc.metadata["source"])

        # Check if the result is not empty (using the correct key)
        self.assertIsNotNone(result, "Retriever returned no result")
        self.assertIn("answer", result, "Result does not contain 'answer' key")
        self.assertGreater(len(result['answer']), 0, "Retriever returned empty answer")  # Check 'answer' length

if __name__ == "__main__":
    unittest.main()
