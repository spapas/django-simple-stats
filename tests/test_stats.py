from django.test import TestCase
from .stats import PollStats, POLL_STATS_RESULT
from .models import Poll, Choice

class StatsTest(TestCase):
    def setUp(self):
        p1 = Poll.objects.create(question="Q1?", pub_date="2023-01-01")
        Choice.objects.create(poll=p1, choice_text="A", votes=2, kind="a")
        Choice.objects.create(poll=p1, choice_text="B", votes=1, kind="b")
        Choice.objects.create(poll=p1, choice_text="C", votes=1, )

        p2 = Poll.objects.create(question="Q2?", pub_date="2022-01-01")
        Choice.objects.create(poll=p2, choice_text="A2", votes=3, kind="a")
        Choice.objects.create(poll=p2, choice_text="B2", votes=1, kind="b")
        Choice.objects.create(poll=p2, choice_text="C2", votes=1, )

        choices_qs = Choice.objects.all()
        self.stats = PollStats(choices_qs)

    def test_stats(self):
        stats = self.stats.get_stats()
        
        for s, d in zip(stats, POLL_STATS_RESULT):
            self.assertEqual(s, d)
