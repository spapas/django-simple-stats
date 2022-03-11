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
                'label': 'Σύνολο',
                'kind': 'query_aggregate_single',
                'method': 'count',
                'field': 'id',
            },
            {
                'label': 'Ανά Πλοηγική Υπηρεσία',
                'kind': 'query_aggregate',
                'method': 'count',
                'field': 'pilot_authority__name',
            }
            {
                'label': 'Ανά κατάσταση',
                'kind': 'choice_aggregate',
                'method': 'count',
                'field': 'status',
                'choices': models.REQUEST_STATUS_CHOICES,
            },
            {
                'label': 'Ανά έτος δημιουργίας',
                'kind': 'query_aggregate_date',
                'method': 'count',
                'field': 'created_on',
                'what': 'year',
                
            },
            {
                'label': 'Ανά net tonnage',
                'kind': 'query_aggregate_buckets',
                'method': 'count',
                'field': 'net_tonnage',
                'buckets': [100_00, 50_00, 1_000, 500, 0]
            }
        ]

    def my_view(request):
        qs = TestModel.objects.all()

        stats = get_stats(qs, STATS_CFG)
        return render(request, 'my_template.html', {'stats': stats})



Changelog
=========

* v.0.1.0: Initial version
