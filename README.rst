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

    def my_view(request):
        qs = TestModel.objects.all()

        stats = get_stats(qs, stats_cfg)
        return render(request, 'my_template.html', {'stats': stats})



### Changelog

* v.0.1.0: Initial version
