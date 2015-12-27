.. Kicking page rebuild 2014-10-30 20:55:46
.. _planning:

Retrieving Plan Information
=============================

Getting list of all plans
---------------------------
.. sourcecode:: http

  GET /plans HTTP/1.1

.. sourcecode:: http

  HTTP/1.1 200 OK

Sorting
~~~~~~~
Plans retuned are sorted by modification time.

Limiting number of Plans returned
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can control the number of `data` entries in the plans feed (batch
size) with `limit` parameter. If not specified, data is being returned in
batches of 100 elements.

Batching
~~~~~~~~

The response contains `next_page` element with the following properties:

:offset:
    This is the parameter you have to add to the original request you made
    to get next page.

:path:
    This is path section of URL with original parameters and `offset`
    parameter added/replaced above.

:uri:
    The full version of URL for next page.

If next page request returns no data (i.e. empty array) then there is little
sense in fetching further pages.

Synchronizing
~~~~~~~~~~~~~

It is often necessary to be able to syncronize central database changes with
other database (we'll call it "local").  The default sorting "by
modification date" together with Batching mechanism allows one to implement
synchronization effectively.  The synchronization process can go page by
page until there is no new data returned.  Then the synchronizer has to
pause for a while to let central database register some changes and attempt
fetching subsequent page.  The `next_page` guarantees that all changes
from the last request are included in the new batch.

The safe frequency of synchronization requests is once per 5 minutes.
 
Reading the individual plan information
-----------------------------------------
.. sourcecode:: http

  GET /plans/64e93250be76435397e8c992ed4214d1 HTTP/1.1

.. sourcecode:: http

  HTTP/1.1 200 OK