import json
import unittest
from unittest.mock import patch
import numpy as np
from config import ROOT
from rag import (load_guide, cosine_top_k, validate_answer, UNKNOWN,
                 RagError, build_index, answer_question)


class RagTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT/'knowledge_base.json').read_text(encoding='utf-8')
        self.entries = load_guide(self.raw)

    def test_data_contract(self):
        self.assertEqual(len(self.entries), 16)
        self.assertEqual(sum(e['category'] != 'guide' for e in self.entries), 12)
        invalid = json.loads(self.raw)
        invalid[1]['id'] = invalid[0]['id']
        with self.assertRaises(RagError):
            load_guide(json.dumps(invalid))

    def test_cosine_is_normalized_and_stably_sorted(self):
        ranked = cosine_top_k([1, 0], [[2, 0], [1, 1], [-4, 0]])
        self.assertEqual([i for i, _ in ranked], [0, 1, 2])
        self.assertAlmostEqual(ranked[1][1], 2**-0.5)
        with self.assertRaises(RagError):
            cosine_top_k([0, 0], [[1, 0]])

    def test_citations_must_match_retrieved_ids(self):
        retrieved = [{'entry': self.entries[0], 'score': 1}]
        for answer, ids in [('Thông tin [G99]', ['G99']), ('Thông tin', ['G01']), ('Thông tin [G01]', ['G02'])]:
            result = validate_answer({'answerable': True, 'answer': answer, 'citations': ids}, retrieved)
            self.assertEqual(result[0], UNKNOWN)
        good = validate_answer({'answerable': True, 'answer': 'Thông tin [G01]', 'citations': ['G01']}, retrieved)
        self.assertEqual(good[2], 'answered')

    def test_unknown_never_keeps_generated_guess(self):
        self.assertEqual(validate_answer({'answerable': False, 'answer': 'Giá 999 đồng', 'citations': []}, [])[0], UNKNOWN)

    def test_cached_index_and_changed_content(self):
        build_index.clear()
        vectors = np.ones((16, 3))
        with patch('rag.OllamaClient.embed', return_value=vectors) as embed:
            build_index(self.raw, 'http://test.invalid')
            build_index(self.raw, 'http://test.invalid')
            self.assertEqual(embed.call_count, 1)
            build_index(self.raw+'\n', 'http://test.invalid')
            self.assertEqual(embed.call_count, 2)
        build_index.clear()

    def test_empty_question_never_calls_server(self):
        with self.assertRaises(RagError):
            answer_question('   ', None, None)


if __name__ == '__main__':
    unittest.main()
