from simple_stats import (
    StatSet,
    QueryAggregateSingleStat,
    QueryAggregateStat,
    QueryAggregateDateStat,
    QueryAggregateExtractDateStat,
    QueryAggregateBucketsStat,
    ChoiceAggregateStat,
    ChoiceAggregateNullStat,
)
from .models import CHOICE_CHOICES


class MyStats(StatSet):
    st1 = QueryAggregateSingleStat()
    st2 = QueryAggregateStat(label="st2-label")
    st3 = QueryAggregateDateStat(what="year")
    st4 = QueryAggregateBucketsStat(aggr_field="f")
    st5 = ChoiceAggregateStat(choices=[(1, 1), (2, 2)])
    st6 = ChoiceAggregateNullStat(choices=[(1, 1), (2, 2)])


MY_STATS_DICT = [
    {
        "field": "st1",
        "kind": "query_aggregate_single",
        "limit": None,
        "label": "st1",
        "aggr_field": None,
        "method": "count",
        "name": "st1",
    },
    {
        "field": "st2",
        "kind": "query_aggregate",
        "limit": None,
        "label": "st2-label",
        "aggr_field": None,
        "method": "count",
        "name": "st2",
    },
    {
        "field": "st3",
        "kind": "query_aggregate_date",
        "limit": None,
        "label": "st3",
        "aggr_field": None,
        "method": "count",
        "name": "st3",
        "what": "year",
    },
    {
        "field": "st4",
        "kind": "query_aggregate_buckets",
        "limit": None,
        "label": "st4",
        "aggr_field": "f",
        "method": "count",
        "name": "st4",
    },
    {
        "field": "st5",
        "kind": "choice_aggregate",
        "limit": None,
        "label": "st5",
        "aggr_field": None,
        "method": "count",
        "name": "st5",
        "choices": [(1, 1), (2, 2)],
    },
    {
        "field": "st6",
        "kind": "choice_aggregate_with_null",
        "limit": None,
        "label": "st6",
        "aggr_field": None,
        "method": "count",
        "name": "st6",
        "choices": [(1, 1), (2, 2)],
    },
]


class PollStats(StatSet):
    id = QueryAggregateSingleStat(label="Choice count")
    vote_sum = QueryAggregateSingleStat(label="Vote sum", method="sum", field="votes")
    vote_sum_per_poll = QueryAggregateStat(
        label="Vote sum per poll",
        method="sum",
        field="poll__question",
        aggr_field="votes",
    )
    vote_sum_per_year = QueryAggregateDateStat(
        method="sum", field="poll__pub_date", aggr_field="votes", what="year"
    )
    vote_sum_per_month_year = QueryAggregateDateStat(
        method="sum", field="poll__pub_date", aggr_field="votes", what="month"
    )
    vote_sum_per_month = QueryAggregateExtractDateStat(
        method="sum", field="poll__pub_date", aggr_field="votes", what="month"
    )
    vote_sum_per_kind = ChoiceAggregateStat(
        method="sum", field="kind", aggr_field="votes", choices=CHOICE_CHOICES
    )
    vote_sum_per_kind_null = ChoiceAggregateNullStat(
        method="sum", field="kind", aggr_field="votes", choices=CHOICE_CHOICES
    )
    vote_buckets = QueryAggregateBucketsStat(
        field="votes",
        buckets=[2, 1],
    )


POLL_STATS_RESULT = [
    {"headers": None, "label": "Choice count", "values": [], "value": 6},
    {"headers": None, "label": "Vote sum", "values": [], "value": 9},
    {
        "headers": None,
        "label": "Vote sum per poll",
        "values": [("Q2?", 5), ("Q1?", 4)],
        "value": None,
    },
    {
        "headers": None,
        "label": "vote_sum_per_year",
        "values": [("2022", 5), ("2023", 4)],
        "value": None,
    },
    {
        "headers": None,
        "label": "vote_sum_per_month_year",
        "values": [("2022-01", 5), ("2023-01", 4)],
        "value": None,
    },
    {
        "headers": None,
        "label": "vote_sum_per_month",
        "values": [
            (1, 9),
        ],
        "value": None,
    },
    {
        "headers": None,
        "label": "vote_sum_per_kind",
        "values": [("A", 5), ("B", 2)],
        "value": None,
    },
    {
        "headers": None,
        "label": "vote_sum_per_kind_null",
        "values": [("A", 5), ("B", 2), (None, 2)],
        "value": None,
    },
    {
        "headers": None,
        "label": "vote_buckets",
        "values": [(">=2", 2), (">=1", 6)],
        "value": None,
    },
]
