.. _usersguide_templates:

Template and Runtime Files
==========================

As described in (coupling section), SaltProc uses file-based coupling to
iterface with depletion solvers. A user provides the template input file(s),
and SaltProc makes a temporary copy used for running depletion steps that it
can modify and update as needed.

Serpent 2 Template Files
------------------------
A valid Serpent 2 template input file must have at least the following:

  - Non-burnable materials instantiated directly in the file
  - Burnable materials linked via the ``include`` card.


So a minimal example would look like:
(fill in)

For best results, we recommend users also include neutron decay,
delayed fission yield, and spontaneous fission yield sublibraries.
Users looking to further configure their input file should see
Serpent 2's `input syntax manual`_. 

.. _input syntax manual: https://serpent.vtt.fi/mediawiki/index.php/Installing_and_running_Serpent#Setting_up_the_data_libraries


OpenMC Template Files
---------------------
Any valid :class:`~openmc.model.Model` object can be exported into a set of
template files that will work with SaltProc. See the `OpenMC docpages`_ for more
info.


.. _input syntax manual: https://docs.openmc.org/..
