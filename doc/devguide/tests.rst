.. _devguide_tests:

Test Suite
==========

The SaltProc test suite uses the JEFF 3.1.2 library for Serpent2 integration
tests, and the ENDF/B VII.1 library for OpenMC integration tests. You can
obtain the JEFF 3.1.2 library by running the `process_j312.bash` script
under `scripts/xsdata`, and you can obtain the ENDF/B VII.1 library
for OpenMC from `this_` link, which you can also find on
`openmc.org <openmc.org/official-data-libraries/>`_. The test suite
requires the pytest_ package.

.. _this: https://anl.box.com/shared/static/9igk353zpy8fn9ttvtrqgzvw1vtejoz6.xz
.. _pytest: https://docs.pytest.org

Whenever a new feature or function is added, a test should also be added
for that feature.
