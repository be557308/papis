import os
import sys
import papis.api
import papis.config
import papis.document
import papis.database
import unittest
import tests
import tempfile


class DatabaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        backend = papis.config.get('database-backend')
        tests.setup_test_library()
        papis.config.set('database-backend', backend)

        libdir = papis.config.get_lib().paths[0]
        assert(os.path.exists(libdir))
        assert(papis.config.get_lib_name() == tests.get_test_lib_name())

        database = papis.database.get(papis.config.get_lib())
        database.clear()
        database.initialize()
        assert(database is not None)

    def test_get_lib(self):
        database = papis.database.get()
        self.assertTrue(database.get_lib() == papis.config.get_lib_name())

    def test_get_dir(self):
        database = papis.database.get()
        self.assertTrue(
            database.get_dirs() == papis.config.get_lib_dirs()
        )

    def test_check_database(self):
        database = papis.database.get()
        self.assertTrue(database is not None)
        self.assertTrue(database.get_lib() == tests.get_test_lib_name())

    def test_update(self):
        database = papis.database.get()
        doc = database.get_all_documents()[0]
        self.assertTrue(doc is not None)
        doc['title'] = 'test_update test'
        doc.save()
        database.update(doc)
        docs = database.query_dict({'title': 'test_update test'})
        self.assertTrue(len(docs) == 1)
        doc = docs[0]
        self.assertTrue(doc is not None)
        self.assertTrue(doc['title'] == 'test_update test')

    def test_query_dict(self):
        database = papis.database.get()
        doc = database.get_all_documents()[0]
        doc['author'] = 'test_query_dict'
        doc.save()
        database.update(doc)
        docs = database.query_dict(
            {'title': doc['title'], 'author': doc['author']}
        )
        self.assertTrue(len(docs) == 1)

    def test_delete(self):
        database = papis.database.get()
        docs = database.get_all_documents()
        Ni = len(docs)
        self.assertTrue(Ni > 1)
        database.delete( docs[0] )
        docs = database.get_all_documents()
        Nf = len(docs)
        self.assertTrue(Ni - Nf == 1)

    def test_initialize(self):
        # trying to initialize again should do nothing
        papis.database.get().initialize()

    def test_get_all_documents(self):
        database = papis.database.get()
        docs = database.get_all_documents()
        self.assertTrue(len(docs) > 0)

    def test_add(self):
        database = papis.database.get()
        docs = database.get_all_documents()
        N = len(docs)
        newdocs = [
            papis.document.from_data(data)
            for data in tests.test_data
        ]
        for j,doc in enumerate(newdocs):
            doc.set_folder(tempfile.mkdtemp())
            doc['title'] = 'lorem ipsum ' + str(j)
            doc.save()
            folder = os.path.join(
                database.get_dirs()[0],
                'new',
                str(j+N)
            )
            papis.document.move(doc, folder)
            assert(os.path.exists(doc.get_main_folder()))
            database.add(doc)
        docs = database.get_all_documents()
        self.assertEqual(len(docs), N*2)

    def test_clear(self):
        database = papis.database.get()
        database.clear()
        database.initialize()
        self.test_get_all_documents()

    def test_all_query_string(self):
        database = papis.database.get()
        self.assertEqual(
            papis.database.get_all_query_string(),
            database.get_all_query_string()
        )

    def test_backend_name(self):
        self.assertTrue(papis.database.get().get_backend_name() is not None)

    def test_backend(self):
        self.assertEqual(
            papis.config.get('database-backend'),
            papis.database.get().get_backend_name()
        )
