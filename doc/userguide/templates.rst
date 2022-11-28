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
  - Burnable materials linked via the ```include`` card.`_
  - The burnable materials should all use the ``fix`` option in the ```mat`` card`_.
  - Neutron particle parameters set via the ```set pop`` card`_.
  - Spontaneous fission yielf sublibray via the ```set sfylib`` card`_

Template input files should also have the following (they are not neccesary if
the user has used the appropriate environment variables to specify them. See
the links for each card for more details):

  - The cross section data directory file via the ```set acelib`` card`_.
  - Decay sublibraries set via the ```set declib`` card`_.
  - Delayed fission yield sublibrary via the ```set nfylib`` card`_.


So a minimal example assuming the without the use of environment variables would look like:

.. code-block:: cfg 

   % Cross section libraries
   set acelib /home/user/xsdata/endfb71/endfb71.xsdata

   %% SaltProc will write include card for geometry file here


   % Sublibraries
   set declib /home/user/xsdata/endfb71/endfb71.dec
   set sfylib /home/user/xsdata/endfb71/endfb71.sfy
   set nfylib /home/user/xsdata/endfb71/endfb71.nfy

   % Include burnable materials
   include /home/user/msbr_model/burnable_mats.ini

   % Set neutron population
   set pop 1000 40 10


And the material file containing burnable materials would look like:

.. code-block:: cfg 

   mat uo2 -10.0 vol 0.554 burn 1 fix 82c 900
       8016.82c  1.0
       92234.82c 0.0004
       92235.82c 0.043
       92238.82c 0.9564
       92236.82c 0.0002


Users looking further cutomize the depletion step should read  Serpent 2's
`input syntax manual`_, in particular the ```set bumode`` card`_ and the
```set pcc`` card`_.

.. _``mat`` card: https://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#mat
.. _``set acelib`` card: https://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#set_acelib
.. _``set declib`` card: https://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#set_declib
.. _``set sfylib`` card: https://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#set_sfylib
.. _``set nfylib`` card: https://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#set_nfylib
.. _``include`` card: https://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#include
.. _``set bumode`` card: https://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#set_bumode
.. _``set pcc`` card: https://serpent.vtt.fi/mediawiki/index.php/Input_syntax_manual#set_pcc
.. _input syntax manual: https://serpent.vtt.fi/mediawiki/index.php/Installing_and_running_Serpent#Setting_up_the_data_libraries


OpenMC Template Files
---------------------
Any valid :class:`~openmc.model.Model` object can be exported into a set of
template files that will work with SaltProc. See the `OpenMC docpages`_ for more
info.


.. _input syntax manual: https://docs.openmc.org/..
