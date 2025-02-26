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
from django.db.models.functions import Trunc, Extract
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

def get_ordering_function(ordering_type):
    valid_orderings = ['value_desc', 'value_asc', 'label_desc', 'label_asc']
    
    if ordering_type not in valid_orderings:
        raise ValueError(f"Unknown ordering type: '{ordering_type}'. "
                         f"Valid options are: {', '.join(valid_orderings)}")
    
    def order_values(values):
        if not values:
            return values
            
        if ordering_type == 'value_desc':
            return values
        elif ordering_type == 'value_asc':
            return sorted(values, key=lambda x: x[1])
        elif ordering_type == 'label_desc':
            return sorted(values, key=lambda x: x[0], reverse=True)
        elif ordering_type == 'label_asc':
            return sorted(values, key=lambda x: x[0])
    
    return order_values

def get_choice_label(choices, value):
    for c in choices:
        if c[0] == value:
            return c[1]


def get_stats(qs, cfg):
    r = []
    for c in cfg:
                
        method = c["method"] if "method" in c and c["method"] else "count"
        aggr_function = get_aggregate_function(method)
        field = c["field"]
        aggr_field = c.get("aggr_field") or field
        limit = c.get("limit")
        headers = c.get("headers")
        ordering = c.get("ordering", "value_desc")
        values = []
        list_aggr_field = isinstance(aggr_field, list)
        value = None
        if c["kind"] == "query_aggregate":
            if list_aggr_field:
                annotation = {f"aggr_{f}": aggr_function(f) for f in aggr_field}
            else:
                annotation = {f"aggr_{aggr_field}": aggr_function(aggr_field)}
            values = [
                tuple([z.get(field)] + [z.get(k) for k in annotation.keys()])
                for z in qs.values(field)
                .annotate(**annotation)
                .order_by(field if list_aggr_field else f"-aggr_{aggr_field}")
                if z.get(field) is not None
            ]
        elif c["kind"] in ("query_aggregate_date", "query_aggregate_datetime"):
            def format_date(d, what):
                if not d:
                    return None
                if what == "year":
                    return d.strftime("%Y")
                elif what == "month":
                    return d.strftime("%Y-%m")
                elif what == "day":
                    return d.strftime("%Y-%m-%d")
                elif what == "hour":
                    return d.strftime("%Y-%m-%d %H")
                else:
                    return d

            if list_aggr_field:
                annotation = {f"aggr_{f}": aggr_function(f) for f in aggr_field}
            else:
                annotation = {f"aggr_{aggr_field}": aggr_function(aggr_field)}

            output_field_cls = (
                DateTimeField if c["kind"] == "query_aggregate_datetime" else DateField
            )
            values = [
                tuple([format_date(z["aggr"], c["what"])]
                + [z.get(k) for k in annotation.keys()])
                for z in qs.annotate(
                    aggr=Trunc(field, c["what"], output_field=output_field_cls())
                )
                .values("aggr")
                .annotate(**annotation)
                .order_by(field if list_aggr_field else f"-aggr_{aggr_field}")
                
            ]

        elif c["kind"] in ("query_aggregate_extract_date"):
            
            values = [
                (z["aggr"], z["aggr2"])
                for z in qs.annotate(aggr=Extract(field, c["what"]))
                .values("aggr")
                .annotate(aggr2=aggr_function(aggr_field))
                .order_by("aggr")
            ]

        elif c["kind"] in ["choice_aggregate", "choice_aggregate_with_null"]:
            values = [
                (get_choice_label(c["choices"], x[field]), x["aggr"])
                for x in qs.values(field)
                .annotate(aggr=aggr_function(aggr_field))
                .distinct()
                .order_by(("-aggr"))
                if c["kind"] == "choice_aggregate_with_null"
                or (x.get(field) is not None and x.get(field) != "")
            ]

        elif c["kind"] == "query_aggregate_buckets":
            buckets = c["buckets"]
            field = c["field"]

            params = {}
            for b in buckets:
                if isinstance(b, tuple) and len(b) == 2:
                    label = f"{b[0]}-{b[1]}"
                    filter_criteria = Q(**{
                        f"{field}__gte": b[0],
                        f"{field}__lte": b[1]
                    })
                else:
                    label = f">={b}"
                    filter_criteria = Q(**{f"{field}__gte": b})

                params[label] = aggr_function("pk", filter=filter_criteria)

            values = [(z[0], z[1]) for z in qs.aggregate(**params).items()]


        elif c["kind"] == "query_aggregate_single":
            value = qs.aggregate(aggr=aggr_function(field))["aggr"]

        else:
            raise NotImplementedError("unknown stat kind {}".format(c["kind"]))

        formatter = c.get("formatter")
        if formatter:
            values = [(x[0], formatter(x[1])) for x in values]
            if value:
                value = formatter(value)

        stat = {
            "label": c["label"] if "label" in c and c["label"] else c["field"],
            "values": values[:limit] if limit else values,
            "value": value,
            "headers": headers,
        }
        
        try:
            ordering_function = get_ordering_function(ordering)
            if values:
                stat['values'] = ordering_function(values)
        except ValueError as e:
            print(f"Warning: {e}, using default ordering")
            stat['values'] = sorted(values, key=lambda x: x[1], reverse=True)

        r.append(stat)
    return r


STAT_ALLOWED_FIELDS = {
    "choices",
    "method",
    "what",
    "aggr_field",
    "kind",
    "field",
    "limit",
    "buckets",
    "label",
    "formatter",
    "headers",
    "ordering",
}


class StatBase:
    field = None
    label = None
    aggr_field = None
    limit = None

    def __init__(self, **kwargs):
        for k in kwargs.keys():
            if k not in STAT_ALLOWED_FIELDS:
                raise ValueError("unknown stat field {}".format(k))

        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, "label"):
            self.label = self.field
        if not hasattr(self, "method"):
            self.method = "count"

    def to_dict(self):
        return {k: getattr(self, k) for k in STAT_ALLOWED_FIELDS if hasattr(self, k)}


class QueryAggregateStat(StatBase):
    kind = "query_aggregate"


class QueryAggregateSingleStat(StatBase):
    kind = "query_aggregate_single"


class QueryAggregateDateStat(StatBase):
    kind = "query_aggregate_date"


class QueryAggregateDateTimeStat(StatBase):
    kind = "query_aggregate_datetime"


class QueryAggregateExtractDateStat(StatBase):
    kind = "query_aggregate_extract_date"


class QueryAggregateBucketsStat(StatBase):
    kind = "query_aggregate_buckets"


class ChoiceAggregateStat(StatBase):
    kind = "choice_aggregate"


class ChoiceAggregateNullStat(StatBase):
    kind = "choice_aggregate_with_null"


class BoundStat:
    name = None
    stat = None

    def __init__(self, name, stat):
        self.name = name
        self.stat = stat

    def to_dict(self):
        d = self.stat.to_dict()
        d["name"] = self.name

        if not d["label"]:
            d["label"] = self.name
        if not d["field"]:
            d["field"] = self.name
        return d


class StatSetMetaclass(type):
    def __new__(mcs, name, bases, attrs):
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

        base_stats = OrderedDict(parent_stats)
        base_stats.update(OrderedDict(stats))

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

        self.stats = self.bound_stats
        self.data = data

    def get_stats(self):
        stats_cfg = [s.to_dict() for s in self.stats]
        return get_stats(self.data, stats_cfg)

    def __iter__(self):
        self._istats = self.get_stats()
        self._iidx = 0
        self._imax = len(self._istats)
        return self

    def __next__(self):
        if self._iidx < self._imax:
            self._iidx += 1
            return self._istats[self._iidx - 1]
        raise StopIteration
