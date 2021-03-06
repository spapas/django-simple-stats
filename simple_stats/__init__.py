from django.db.models import Count, Sum, Avg, Min, Max, DateTimeField, When, Case, Q
from django.db.models.functions import (
    Trunc,
)


def get_aggregate_function(name):
    if name == "count":
        return Count
    elif name == "sum":
        return Sum
    elif name == "avg":
        return Avg
    elif name == "min":
        return Min
    elif name == "max":
        return Max
    else:
        raise ValueError("unknown aggregate function")


def get_choice_label(choices, value):
    for c in choices:
        if c[0] == value:
            return c[1]


def get_stats(qs, cfg):
    r = []
    for c in cfg:
        aggr_function = get_aggregate_function(c["method"])
        field = c["field"]
        limit = c.get("limit")
        values = []
        value = None
        if c["kind"] == "query_aggregate":
            values = [
                (z.get(field), z["aggr"])
                for z in qs.values(field)
                .annotate(aggr=aggr_function(field))
                .order_by("-aggr")
                if z.get(field) != None
            ]
        elif c["kind"] == "query_aggregate_date":
            values = [
                (getattr(z["aggr"], c["what"]), z["aggr2"])
                for z in qs.annotate(
                    aggr=Trunc(field, c["what"], output_field=DateTimeField())
                )
                .values("aggr")
                .annotate(aggr2=aggr_function(field))
                .order_by("aggr")
            ]

        elif c["kind"] == "choice_aggregate":
            values = [
                (get_choice_label(c["choices"], x[field]), x["aggr"])
                for x in qs.values(field)
                .annotate(aggr=aggr_function(field))
                .distinct()
                .order_by(("-aggr"))
                if x.get(field) != None
            ]
        elif c["kind"] == "query_aggregate_buckets":
            buckets = c["buckets"]
            params = {
                "> " + str(b): aggr_function("pk", filter=Q(**{field + "__gte": b}))
                for b in buckets
            }

            values = [(z[0], z[1]) for z in qs.aggregate(**params).items()]

        elif c["kind"] == "query_aggregate_single":
            value = qs.aggregate(aggr=aggr_function(field))["aggr"]

        stat = {
            "label": c["label"],
            "values": values[:limit] if limit else values,
            "value": value,
        }
        r.append(stat)
    return r
