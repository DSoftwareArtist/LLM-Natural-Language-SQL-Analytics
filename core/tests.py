from django.test import TestCase
from unittest.mock import patch, MagicMock

from .services import SQLGenerationService


class SQLGenerationServiceTests(TestCase):
    
    def test_format_schema_for_prompt(self):
        schema = {
            'tables': ['users', 'orders'],
            'columns': [
                {'table_name': 'users', 'column_name': 'id', 'data_type': 'integer'},
                {'table_name': 'users', 'column_name': 'name', 'data_type': 'varchar'},
                {'table_name': 'orders', 'column_name': 'id', 'data_type': 'integer'},
                {'table_name': 'orders', 'column_name': 'user_id', 'data_type': 'integer'}
            ]
        }
        
        result = SQLGenerationService.format_schema_for_prompt(schema)
        
        self.assertIn('Table: users', result)
        self.assertIn('Table: orders', result)
        self.assertIn('id (integer)', result)
        self.assertIn('name (varchar)', result)

    def test_format_schema_empty_tables(self):
        schema = {
            'tables': [],
            'columns': []
        }
        
        result = SQLGenerationService.format_schema_for_prompt(schema)
        
        self.assertEqual(result, '')

    def test_format_schema_single_table(self):
        schema = {
            'tables': ['products'],
            'columns': [
                {'table_name': 'products', 'column_name': 'id', 'data_type': 'serial'},
                {'table_name': 'products', 'column_name': 'name', 'data_type': 'varchar'},
                {'table_name': 'products', 'column_name': 'price', 'data_type': 'numeric'}
            ]
        }
        
        result = SQLGenerationService.format_schema_for_prompt(schema)
        
        self.assertIn('Table: products', result)
        self.assertIn('id (serial)', result)
        self.assertIn('price (numeric)', result)

    @patch('core.services.SQLGenerationService.get_llm')
    def test_generate_sql_success(self, mock_get_llm):
        mock_chain = MagicMock()
        mock_chain.run.return_value = "SELECT * FROM users WHERE id = 1"
        
        with patch('core.services.LLMChain', return_value=mock_chain):
            result = SQLGenerationService.generate_sql("Get all users", "Schema info")
        
        self.assertIn("SELECT", result)

    @patch('core.services.SQLGenerationService.get_llm')
    def test_generate_sql_strips_sql_prefix(self, mock_get_llm):
        mock_chain = MagicMock()
        mock_chain.run.return_value = "```sql\nSELECT * FROM users\n```"
        
        with patch('core.services.LLMChain', return_value=mock_chain):
            result = SQLGenerationService.generate_sql("Get users", "Schema")
        
        self.assertTrue(result.startswith("SELECT"))

    @patch('core.services.SQLGenerationService.get_llm')
    def test_generate_sql_strips_sql_prefix_lowercase(self, mock_get_llm):
        mock_chain = MagicMock()
        mock_chain.run.return_value = "sql\nSELECT * FROM users"
        
        with patch('core.services.LLMChain', return_value=mock_chain):
            result = SQLGenerationService.generate_sql("Get users", "Schema")
        
        self.assertTrue(result.startswith("SELECT"))

    @patch('core.services.SQLGenerationService.get_llm')
    def test_generate_sql_strips_backticks(self, mock_get_llm):
        mock_chain = MagicMock()
        mock_chain.run.return_value = "SELECT * FROM orders"
        
        with patch('core.services.LLMChain', return_value=mock_chain):
            result = SQLGenerationService.generate_sql("Get orders", "Schema")
        
        self.assertEqual(result, "SELECT * FROM orders")

    @patch('core.services.SQLGenerationService.get_llm')
    def test_generate_sql_insert_statement(self, mock_get_llm):
        mock_chain = MagicMock()
        mock_chain.run.return_value = "INSERT INTO users (name) VALUES ('John')"
        
        with patch('core.services.LLMChain', return_value=mock_chain):
            result = SQLGenerationService.generate_sql("Insert John", "Schema")
        
        self.assertIn("INSERT", result)


class EmbeddingServiceUnitTests(TestCase):
    
    @patch('core.services.EmbeddingService.get_model')
    def test_embed_text_returns_list(self, mock_get_model):
        from .services import EmbeddingService
        
        mock_model = MagicMock()
        mock_array = MagicMock()
        mock_array.tolist.return_value = [0.1, 0.2, 0.3, 0.4]
        mock_model.encode.return_value = mock_array
        mock_get_model.return_value = mock_model
        
        result = EmbeddingService.embed_text("test text")
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)
        mock_model.encode.assert_called_once()

    @patch('core.services.SentenceTransformer')
    def test_embed_text_default_model_name(self, mock_transformer):
        from .services import EmbeddingService
        
        mock_model = MagicMock()
        mock_array = MagicMock()
        mock_array.tolist.return_value = [0.1]
        mock_model.encode.return_value = mock_array
        mock_transformer.return_value = mock_model
        
        EmbeddingService._model = None
        
        EmbeddingService.embed_text("test")
        
        mock_transformer.assert_called_once_with('all-MiniLM-L6-v2')

    @patch('core.services.EmbeddingService.get_model')
    def test_embed_text_model_cached(self, mock_get_model):
        from .services import EmbeddingService
        
        mock_model = MagicMock()
        mock_array = MagicMock()
        mock_array.tolist.return_value = [0.1]
        mock_model.encode.return_value = mock_array
        mock_get_model.return_value = mock_model
        
        EmbeddingService.embed_text("test")
        EmbeddingService.embed_text("test2")
        
        self.assertEqual(mock_model.encode.call_count, 2)

    @patch('core.services.EmbeddingService.get_model')
    def test_embed_documents_multiple_texts(self, mock_get_model):
        from .services import EmbeddingService
        
        mock_model = MagicMock()
        
        embedding1 = MagicMock()
        embedding1.tolist.return_value = [0.1, 0.2]
        embedding2 = MagicMock()
        embedding2.tolist.return_value = [0.3, 0.4]
        embedding3 = MagicMock()
        embedding3.tolist.return_value = [0.5, 0.6]
        
        mock_model.encode.return_value = [embedding1, embedding2, embedding3]
        mock_get_model.return_value = mock_model
        
        result = EmbeddingService.embed_documents(["text1", "text2", "text3"])
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], [0.1, 0.2])
        self.assertEqual(result[1], [0.3, 0.4])
        self.assertEqual(result[2], [0.5, 0.6])
