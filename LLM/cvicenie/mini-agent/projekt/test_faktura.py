import unittest

from faktura import celkom, medzisucet

POLOZKY = [
    {"nazov": "licencia", "cena": 100.0, "mnozstvo": 2},
    {"nazov": "podpora", "cena": 50.0, "mnozstvo": 1},
]


class TestFaktura(unittest.TestCase):
    def test_medzisucet(self):
        self.assertEqual(medzisucet(POLOZKY), 250.0)

    def test_bez_zlavy(self):
        self.assertEqual(celkom(POLOZKY), 307.5)

    def test_zlava_10_percent(self):
        self.assertEqual(celkom(POLOZKY, zlava_percento=10), 276.75)

    def test_zlava_najviac_50_percent(self):
        self.assertEqual(celkom(POLOZKY, zlava_percento=80), 153.75)


if __name__ == "__main__":
    unittest.main()
