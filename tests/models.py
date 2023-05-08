from django.db import models
CHOICE_CHOICES = (("a", "A"), ("b", "B"), ("c", "C"))

class Poll(models.Model):
    question = models.CharField(max_length=256)
    pub_date = models.DateTimeField("date published")


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=256)
    votes = models.IntegerField(default=0)
    kind = models.CharField(max_length=32, choices=CHOICE_CHOICES)
