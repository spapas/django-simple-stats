from django.db.models import (
    Count,
    Sum,
    Avg,
    Min,
    Max,
    DateField,
    DateTimeField,
    When,
    Case,
    Q,
)
from django.db.models.functions import (
    Trunc,
)
import copy
from collections import OrderedDict


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
        aggr_field = c.get("aggr_field") or field
        limit = c.get("limit")
        values = []
        value = None
        if c["kind"] == "query_aggregate":
            values = [
                (z.get(field), z["aggr"])
                for z in qs.values(field)
                .annotate(aggr=aggr_function(aggr_field))
                .order_by("-aggr")
                if z.get(field) is not None
            ]
        elif c["kind"] in ("query_aggregate_date", "query_aggregate_datetime"):
            output_field_cls = (
                DateTimeField if c["kind"] == "query_aggregate_datetime" else DateField
            )
            values = [
                (getattr(z["aggr"], c["what"]), z["aggr2"])
                for z in qs.annotate(
                    aggr=Trunc(field, c["what"], output_field=output_field_cls())
                )
                .values("aggr")
                .annotate(aggr2=aggr_function(aggr_field))
                .order_by("aggr")
            ]

        elif c["kind"] in ["choice_aggregate", "choice_aggregate_with_null"]:
            values = [
                (get_choice_label(c["choices"], x[field]), x["aggr"])
                for x in qs.values(field)
                .annotate(
                    aggr=aggr_function(
                        aggr_field if c["kind"] == "choice_aggregate" else "pk"
                    )
                )
                .distinct()
                .order_by(("-aggr"))
                if c["kind"] == "choice_aggregate_with_null" or x.get(field) != None
            ]

        elif c["kind"] == "query_aggregate_buckets":
            buckets = c["buckets"]
            params = {
                ">" + str(b): aggr_function("pk", filter=Q(**{field + "__gte": b}))
                for b in buckets
            }

            values = [(z[0], z[1]) for z in qs.aggregate(**params).items()]

        elif c["kind"] == "query_aggregate_single":
            value = qs.aggregate(aggr=aggr_function(field))["aggr"]

        else:
            raise NotImplementedError("unknown stat kind {}".format(c["kind"]))

        stat = {
            "label": c["label"],
            "values": values[:limit] if limit else values,
            "value": value,
        }
        r.append(stat)
    return r


class StatsOptions:
    def __init__(self, options, class_name):
        super().__init__()
        self.empty_text = getattr(options, "empty_text", None)
        self.exclude = getattr(options, "exclude", [])


class StatBase:
    field = None
    label = None
    aggr_field = None
    limit = None

    def __init__(self, field=None, label=None, method="count", **kwargs):
        self.field = field
        self.label = label
        if not label:
            self.label = self.field
        self.method = method
        for k, v in kwargs.items():
            setattr(self, k, v)


class QueryAggregateStat(StatBase):
    kind = "query_aggregate"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class QueryAggregateSingleStat(StatBase):
    kind = "query_aggregate_single"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BoundStat:
    name = None
    stat = None
    field = None
    label = None
    

    def __init__(self, name, stat):
        self.name = name
        self.stat = stat
        if not self.stat.field:
            self.stat.field = self.name
        if not self.stat.label:
            self.stat.label = self.name

    def to_dict(self):
        return {
            "name": self.name,
            "label": self.stat.label,
            "field": self.stat.field,
            "method": self.stat.method,
            "kind": self.stat.kind,
            "aggr_field": self.stat.aggr_field,
            "limit": self.stat.limit,
        }


class StatSetMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        attrs["_meta"] = opts = StatsOptions(attrs.get("Meta", None), name)

        stats = []
        for attr_name, attr in attrs.items():
            if isinstance(attr, StatBase):
                stats.append((attr_name, attr))
            else:
                pass

        parent_stats = []
        for base in reversed(bases):
            if hasattr(base, "base_stats"):
                parent_stats = list(base.base_stats.items()) + parent_stats
        print(parent_stats)
        base_stats = OrderedDict(parent_stats)
        base_stats.update(OrderedDict(stats))

        for exclusion in opts.exclude:
            if exclusion in base_stats:
                base_stats.pop(exclusion)

        attrs["base_stats"] = base_stats
        attrs["bound_stats"] = [
            BoundStat(field_name, stat) for field_name, stat in base_stats.items()
        ]

        return super().__new__(mcs, name, bases, attrs)


class StatSet(metaclass=StatSetMetaclass):
    def __init__(self, data=None):
        super().__init__()
        if data is None:
            raise TypeError(f"Argument data to {type(self).__name__} is required")

        self.stats = copy.deepcopy(type(self).bound_stats)
        self.data = data

    def get_stats(self):
        stats_cfg = [s.to_dict() for s in self.stats]
        return get_stats(self.data, stats_cfg)
