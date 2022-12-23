=======
History
=======

0.1.6 (2022-12-23)
------------------
* changed rontrib_clear to hopefully avoid segfault occuring after many resets
  the diagnosis was using lu_delete instead of lu_done. tested on mac and linux.

0.1.5 (2022-10-26)
------------------
* fixed bug from updated radiance where calcontext was not getting
  reinitialized after rcontrib.reset()
* added basic usable renderer objects (without raytraverse)

0.1.4 (2022-09-27)
------------------
* updated radiance

0.1.3 (2022-07-05)
------------------
* error messages in linux

0.1.2 (2022-05-19)
------------------
* added color-channel support

0.1.1 (2022-04-28)
------------------
* added scene property to render objects available from python
* updated to radiance db4988bb 2022-04-24

0.1.0 (2022-04-14)
------------------

* split from main raytraverse module.
