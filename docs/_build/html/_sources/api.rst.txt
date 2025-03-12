API Reference
============

This page provides detailed documentation for the Metric Query Library API.

metric_query_library
------------------

.. automodule:: metric_query_library
   :members:
   :undoc-members:
   :show-inheritance:

metric_query_library.transformations
----------------------------------

.. automodule:: metric_query_library.transformations
   :members:
   :undoc-members:
   :show-inheritance:

metric_query_library.label_ops
----------------------------

.. automodule:: metric_query_library.label_ops
   :members:
   :undoc-members:
   :show-inheritance:

metric_query_library.type_defs
----------------------------

.. automodule:: metric_query_library.type_defs
   :members:
   :undoc-members:
   :show-inheritance:

metric_query_library.validation
-----------------------------

.. automodule:: metric_query_library.validation
   :members:
   :undoc-members:
   :show-inheritance:

Rust API
-------

The following functions are implemented in Rust and exposed to Python:

.. note::
   These functions are documented here for completeness, but they are typically accessed through the Python API described above.

Core Transformations
~~~~~~~~~~~~~~~~~~~

.. py:function:: metric_query_library._rust.moving_average(metric, window_size)

   Calculate the moving average of a metric over a specified window size.

   :param dict metric: The metric to transform
   :param int window_size: The size of the moving average window
   :return: A new metric with the moving average values
   :rtype: dict

.. py:function:: metric_query_library._rust.rate(metric)

   Calculate the rate of change of a metric.

   :param dict metric: The metric to transform
   :return: A new metric with the rate values
   :rtype: dict

.. py:function:: metric_query_library._rust.sum(metrics)

   Sum multiple metrics together.

   :param list metrics: A list of metrics to sum
   :return: A new metric with the summed values
   :rtype: dict

Label Operations
~~~~~~~~~~~~~~

.. py:function:: metric_query_library._rust.filter_by_label(metrics, labels)

   Filter metrics by label.

   :param list metrics: A list of metrics to filter
   :param dict labels: A dictionary of labels to filter by
   :return: A list of metrics that match the labels
   :rtype: list

.. py:function:: metric_query_library._rust.group_by_label(metrics, label_keys)

   Group metrics by label.

   :param list metrics: A list of metrics to group
   :param list label_keys: A list of label keys to group by
   :return: A dictionary of grouped metrics
   :rtype: dict