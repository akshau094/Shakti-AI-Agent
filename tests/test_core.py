import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from shakti.core import Store, Workspace, answer, code_agent, extract, ingest, retrieve


class FakeModel:
    def embed(self, text, query=False):
        return [1.0, 0.0] if 'apple' in text.lower() else [0.0, 1.0]

    def chat(self, messages, model=None, structured=False):
        return 'Local answer'


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root / 'memory.sqlite3')
        self.model = FakeModel()
        self.workspace = Workspace(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_memory_persists_and_isolates_projects(self):
        self.store.remember('a', 'Use Python')
        self.store.add_message('a', 'user', 'Hello')
        reopened = Store(self.store.path)
        self.assertEqual(reopened.memories('a')[0][1], 'Use Python')
        self.assertEqual(reopened.history('a')[0]['content'], 'Hello')
        self.assertEqual(reopened.history('b'), [])
        reopened.clear('a')
        self.assertEqual(reopened.memories('a'), [])

    def test_ingest_retrieval_replaces_and_deduplicates(self):
        doc = self.root / 'fruit.txt'
        doc.write_text('Apple trees need sunlight.', encoding='utf-8')
        self.assertEqual(ingest(self.store, self.model, 'a', doc), 1)
        self.assertEqual(ingest(self.store, self.model, 'a', doc), 0)
        self.assertIn('Apple trees', retrieve(self.store, self.model, 'a', 'apple'))
        self.assertEqual(retrieve(self.store, self.model, 'b', 'apple'), '')
        doc.write_text('Bananas are yellow.', encoding='utf-8')
        ingest(self.store, self.model, 'a', doc)
        self.assertNotIn('Apple trees', retrieve(self.store, self.model, 'a', 'apple'))

    def test_failed_embedding_preserves_existing_index(self):
        doc = self.root / 'fruit.txt'
        doc.write_text('Apple', encoding='utf-8')
        ingest(self.store, self.model, 'a', doc)
        doc.write_text('Changed', encoding='utf-8')
        with patch.object(self.model, 'embed', side_effect=RuntimeError('offline')):
            with self.assertRaises(RuntimeError):
                ingest(self.store, self.model, 'a', doc)
        self.assertIn('Apple', retrieve(self.store, self.model, 'a', 'apple'))

    def test_traversal_credentials_and_absolute_paths_rejected(self):
        for path in ['../escape.py', '.env', '.git/config', '.aws/credentials', str(self.root/'x.py'), 'C:relative.py']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.workspace.safe(path)

    def test_proposals_require_apply_and_detect_stale_content(self):
        file = self.root / 'main.py'
        file.write_text('print(1)\n', encoding='utf-8')
        proposal = self.workspace.proposal('main.py', 'print(2)\n')
        self.assertEqual(file.read_text(), 'print(1)\n')
        file.write_text('print(3)\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.workspace.apply(proposal)
        proposal = self.workspace.proposal('main.py', 'print(4)\n')
        with patch('shakti.core.DATA', self.root/'backups-data'):
            self.workspace.apply(proposal)
        self.assertEqual(file.read_text(), 'print(4)\n')
        self.assertTrue(list((self.root/'backups-data').rglob('main.py')))

    def test_agent_inspects_and_proposes_without_writing(self):
        file = self.root / 'calc.py'
        file.write_text('def add(a,b): return a-b\n', encoding='utf-8')
        actions = [{'action': 'read', 'path': 'calc.py'},
                   {'action': 'propose', 'path': 'calc.py', 'content': 'def add(a,b): return a+b\n'},
                   {'action': 'finish', 'message': 'Review the proposed fix.'}]
        with patch.object(self.model, 'chat', side_effect=[json.dumps(a) for a in actions]):
            proposals, result = code_agent(self.store, self.model, self.workspace, 'Fix add', lambda _: None, threading.Event())
        self.assertEqual(len(proposals), 1)
        self.assertIn('a-b', file.read_text())
        self.assertIn('Review', result)

    def test_answer_saves_both_messages(self):
        self.assertEqual(answer(self.store, self.model, 'a', 'hello'), 'Local answer')
        self.assertEqual(len(self.store.history('a')), 2)

    def test_document_formats(self):
        from docx import Document
        from openpyxl import Workbook
        from pypdf import PdfWriter
        document = Document()
        document.add_paragraph('Apple handbook')
        document.save(self.root/'sample.docx')
        self.assertIn('Apple handbook', extract(self.root/'sample.docx'))
        book = Workbook()
        book.active.append(['Apple', 42])
        book.save(self.root/'sample.xlsx')
        book.close()
        self.assertIn('Apple | 42', extract(self.root/'sample.xlsx'))
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.write(self.root/'scan.pdf')
        with self.assertRaisesRegex(ValueError, 'OCR'):
            extract(self.root/'scan.pdf')
        (self.root/'photo.png').write_bytes(b'not a document')
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            extract(self.root/'photo.png')


if __name__ == '__main__':
    unittest.main()
