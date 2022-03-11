django-simple-stats
-------------------

A django package for creating stats from a query. 

Install it from pip:

``pip install django-simple-stats``

or the latest version from git:

``pip install git+https://github.com/spapas/django-simple-stats``

No other installation is needed.

Then you can use the following in your django app:

.. code-block:: python

    from simple_stats import get_stats

    STATS_CFG = cfg = [
            {
                'label': 'Total',
                'kind': 'query_aggregate_single',
                'method': 'count',
                'field': 'id',
            },
            {
                'label': 'Per authority',
                'kind': 'query_aggregate',
                'method': 'count',
                'field': 'pilot_authority__name',
            }
            {
                'label': 'Per status',
                'kind': 'choice_aggregate',
                'method': 'count',
                'field': 'status',
                'choices': models.STATUS_CHOICES,
            },
            {
                'label': 'Per year',
                'kind': 'query_aggregate_date',
                'method': 'count',
                'field': 'created_on',
                'what': 'year',
                
            },
            {
                'label': 'Per price',
                'kind': 'query_aggregate_buckets',
                'method': 'count',
                'field': 'price',
                'buckets': [100_00, 50_00, 1_000, 500, 0]
            }
        ]

    def my_view(request):
        qs = TestModel.objects.all()

        stats = get_stats(qs, STATS_CFG)
        return render(request, 'my_template.html', {'stats': stats})

The ``stats`` will be an array of dictionaries like the following:

.. code-block:: python

  [
    {'label': 'Total', 'values': [], 'value': 1216}, 
    {'label': 'Per authority', 'values': [('Authority 1', 200), ('Authority 2', 9),   ], 'value': None}, 
    {'label': 'Per status', 'values': [('New', 200), ('Cancel', 0), 'value': None},
    {'label': 'Per year', 'values': [(2021, 582), (2022, 634)], 'value': None}
    {'label': 'Per price', 'values': [('> 5000', 1), ('> 1000', 29), ('> 500', 86), ('> 0', 305)], 'value': None}
  ]
  
You can display this in your template using something like:

.. code-block:: python

  <div class='row'>
    {% for s in stats %}
    <div class='col-md-4 mb-5' style='max-height: 500px; overflow: auto;'>
        <h4>{{ s.label }}</h4>
        {% if s.values %}
            <table class='table table-condensed table-striped small table-sm'>
                {% for v in s.values %}
                    <tr>
                        <td>{{ v.0 }}</td>
                        <td>{{ v.1 }}</td>
                    </tr>
                {% endfor %}
            </table>
        {% else %}
            <b>{{ s.value }}</b>
        {% endif %}
    </div>
    {% endfor %}
  </div>

Usage
=====

The only supported method is the ``get_stats``. It expects a django query and a configuration list. 
Each element of the configuration list is a dictionary with the following attributes:

* label (required): The textual description of this statistic
* kind (required): What kind of aggregate we need. Choices are: ``query_aggregate_single``, ``query_aggregate``, ``choice_aggregate``, ``query_aggregate_date``, ``query_aggregate_buckets``. 
* method (required): The aggregate method. Can be one of ``count``, ``sum``, ``max``, ``min``, ``avg``.
* field (required): The field that the aggreate will run on; use ``__`` for joins i.e ``fiedld1__field2``
* what (optional): Only required for ``query_aggregate_date``, it is eithed ``year``, ``month``, ``day``
* choices (optional): Only required for ``choice_aggregate``, it must be a django choices list 
* buckets (optional): only required for ``query_aggregate_buckets``. Must be a list from the biggest to the lowest value.

See above for a configuration example.

The response will be a list of dictionaries with the following attributes:

* label: Same as the label in the configuration
* value: Will have a value if you use the query_aggregate_single, else will be None 
* values: Will be empty for query_aggregate_single else will be a list of tuples. Each tuple will have two elements, ``(label, value)``

The ``query_aggregate_single`` will run the aggregate function on a field and return a single value. For example you can get the total 
number of rows of your query or the sum of all fields. 

The ``query_aggregate`` will run the aggregate function on a 
field and return the list of values. This is mainly useful for foreign keys and if you've got distinct values in your queries.
For example count the number of rows per user. 
Also it is useful for booleans for example to get the number of rows that have a flag turned on and off. 

The ``choice_aggregate`` is similar to the ``query_aggregate`` but will use a ``choices`` attribute to return better looking values.

The ``query_aggregate_date`` is similar to the ``query_aggregate`` but will return the aggregates on a specific date field; use
``what`` to pass ``year``, ``month``, ``day``.

Finally, the ``query_aggregate_buckets`` is used to create buckets of values. You'll pass the list of buckets and the query will 
return the results that belong in each bucket. The stats module will 
run individual queries with ``field__gte`` for each value. So for example if you pass ``[100, 50, 10]`` and you have a field ``price``
it will run ``price__gte=100``, ``price__gte=50``, ``price__gte=10`` and return the results.




Changelog
=========

* v.0.1.0: Initial version
