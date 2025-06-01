import sqlite3
import unittest
import os

class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db_name = "test_data.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            state TEXT,
                            size INTEGER,
                            length REAL
                        )''')
        self.conn.commit()

    def test_insert_data(self):
        self.c.execute("DELETE FROM data")
        self.c.execute("INSERT INTO data (name, state, size, length) VALUES (?, ?, ?, ?)", ("Alice", "Paris", 5, 15))
        self.c.execute("INSERT INTO data (name, state, size, length) VALUES (?, ?, ?, ?)", ("Bob", "Lyon", 3, 9))
        self.conn.commit()

        self.c.execute("SELECT COUNT(*) FROM data")
        count = self.c.fetchone()[0]
        self.assertEqual(count, 2)

    def test_average_length(self):
        self.c.execute("DELETE FROM data")
        self.c.execute("INSERT INTO data (name, state, size, length) VALUES (?, ?, ?, ?)", ("Alice", "Paris", 5, 15))
        self.c.execute("INSERT INTO data (name, state, size, length) VALUES (?, ?, ?, ?)", ("Bob", "Lyon", 3, 9))
        self.conn.commit()

        self.c.execute("SELECT AVG(length) FROM data")
        avg = self.c.fetchone()[0]
        self.assertAlmostEqual(avg, 12.0)

    def test_clear_db(self):
        self.c.execute("DELETE FROM data")
        self.c.execute("INSERT INTO data (name, state, size, length) VALUES (?, ?, ?, ?)", ("Alice", "Paris", 5, 15))
        self.conn.commit()

        self.c.execute("SELECT COUNT(*) FROM data")
        count_before_clear = self.c.fetchone()[0]
        self.assertGreater(count_before_clear, 0)

        self.c.execute("DELETE FROM data")
        self.conn.commit()

        self.c.execute("SELECT COUNT(*) FROM data")
        count_after_clear = self.c.fetchone()[0]
        self.assertEqual(count_after_clear, 0)

    def test_fetch_data_empty_db(self):
        self.c.execute("DELETE FROM data")
        self.conn.commit()

        self.c.execute("SELECT COUNT(*) FROM data")
        count = self.c.fetchone()[0]
        self.assertEqual(count, 0)

    def test_insert_invalid_data(self):
        self.c.execute("DELETE FROM data")
        self.conn.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            self.c.execute("INSERT INTO data (id) VALUES (NULL)")
            self.conn.commit()

    def test_name_size_calculation(self):
        name = "Jonathan"
        size = len(name)
        self.c.execute("DELETE FROM data")
        self.conn.commit()
        self.c.execute("INSERT INTO data (name, state, size, length) VALUES (?, ?, ?, ?)", (name, "Nice", size, 20))
        self.conn.commit()

        self.c.execute("SELECT size FROM data WHERE name=?", (name,))
        size_from_db = self.c.fetchone()[0]
        self.assertEqual(size_from_db, size)

    def test_duplicate_entries(self):
        self.c.execute("DELETE FROM data")
        self.conn.commit()
        data = ("Alice", "Paris", 5, 15)
        self.c.execute("INSERT INTO data (name, state, size, length) VALUES (?, ?, ?, ?)", data)
        self.c.execute("INSERT INTO data (name, state, size, length) VALUES (?, ?, ?, ?)", data)
        self.conn.commit()

        self.c.execute("SELECT COUNT(*) FROM data WHERE name='Alice'")
        count = self.c.fetchone()[0]
        self.assertEqual(count, 2)

    def test_wrong_data_types(self):
        self.c.execute("DELETE FROM data")
        self.conn.commit()
        with self.assertRaises(sqlite3.InterfaceError):
            self.c.execute("INSERT INTO data (name, state, size, length) VALUES (?, ?, ?, ?)", ("Alice", "Paris", "not_int", "not_float"))
            self.conn.commit()

    def test_size_values_for_graph(self):
        self.c.execute("DELETE FROM data")
        self.c.executemany(
            "INSERT INTO data (name, state, size, length) VALUES (?, ?, ?, ?)",
            [
                ("Anna", "Paris", 4, 12),
                ("Bob", "Lyon", 3, 8),
                ("Charlie", "Marseille", 7, 14)
            ]
        )
        self.conn.commit()

        self.c.execute("SELECT size FROM data")
        sizes = [row[0] for row in self.c.fetchall()]
        self.assertListEqual(sizes, [4, 3, 7])

    def tearDown(self):
        self.conn.close()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

if __name__ == '__main__':
    unittest.main()
