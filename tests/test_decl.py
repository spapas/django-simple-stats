from django.test import TestCase
from .stats import MyStats, MY_STATS_DICT


class DeclarativeTest(TestCase):
    def setUp(self):
        self.stats = MyStats([])

    def test_declarations(self):
        for st, d in zip(self.stats.stats, MY_STATS_DICT):
            self.assertEqual(st.to_dict(), d)
