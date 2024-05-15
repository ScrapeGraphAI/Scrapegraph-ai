Benchmarks
==========

SearchGraph
^^^^^^^^^^^

`SearchGraph` instantiates multiple `SmartScraperGraph` object for each URL and extract the data from the HTML.
A concurrent approach is used to speed up the process and the following table shows the time required for a scraping task with different **batch sizes**.
Only two results are taken into account.

.. list-table:: SearchGraph
   :header-rows: 1

   * - Batch Size
     - Total Time (s)
   * - 1
     - 31.1
   * - 2
     - 33.52
   * - 4
     - 28.47
   * - 16
     - 21.80
