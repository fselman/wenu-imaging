.. MEFPP documentation master file, created by
   sphinx-quickstart on Sun Aug 11 17:49:22 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MEFPP: Multi-Extension FITS Pre-Processing engine
=================================================

MEFPP is a processing software for visual images of mosaic camera.
It is a branch of the original ``wfi`` recipes prepared by Nick Devillard
for the BeoWFI project using the `eclipse package <https://www.eso.org/sci/software/eclipse/>`_. The branch was created
to support the WFI instrument at ESO's La Silla Observatory while the author
was the instrument scientist there.
Then that branch was further modified to port those recipes to OmegaCAM once
the author was transferred to Paranal to become the OmegaCam Instrument Scientist.
One of the characteristic of this package is that it maintains the integrity of
the Multi-Extension FITS files, MEF files, without splitting them into their extensions. Given the
complexity of data management when *reducing* astronomical data it was felt that a
factor of 8 in the number of files produced is too high a price to pay for reducing the
complexity of the software by working with simple FITS files. For OmegaCam the
factor is 32 making the data explosion in reduction even more extreme.

Although this package could be used stand-alone it is really intended to be use
with the package PyCAVI, developed with Lientur Celedon. That package permits
the efficient classification, association, and reduction of mosaic data, specially
those data received as part of a service mode program or programs. These data has
the bad characteristics that a single target observation can be split during
multiple nights spanning months, semesters and even years. In this case the data
management become the main road-block to efficient work. That package take care
of all this, and provide a most needed data visualization interface that permits
the checking of quality control variables. This is specially important when reducing
WFI data which never had strong support from the ESO quality control group in Garching.

An example reduction session can be found in the :doc:`Tutorial </Usage/tutorial>` so that a user can get started quickly.
The program can be used to create the needed calibration files and then reduce the data in one go,
or to first produce the calibration data, and only then reduce the science data with the
calibrations previously determined. 

The mefpp pre-processing engine is written in C and based on the Eclipse and qfits
software package. It modifies extensively the Eclipse wfi package.
The current version is based in eclipse-5.0.0, qfits-5.4.0, amd mefpp-1.5.0. Everything
is distributed together as a tar file.


Note that the :doc:`best starting point </Usage/quick_summary>` is
the guide for those in a hurry.

For detailed step-by-step guide
see :ref:`the tutorial <stepbystepTutorial>` .

An extensive description of the software cab be found at :doc:`/Software/description`.

Admonitions
-----------

Below I show examples of the use of *admonitions*:
note, tip, warning, and danger.

.. note::
   note: Many kids have problems with screen time
   and if you leave them unattended with a
   screen and they have access to things
   like YouTube or games, they may not stay
   focused on the task at hand.

.. tip::
   tip: Many kids have problems with screen time
   and if you leave them unattended with a
   screen and they have access to things
   like YouTube or games, they may not stay
   focused on the task at hand.

.. caution::
   caution: Many kids have problems with screen time
   and if you leave them unattended with a
   screen and they have access to things
   like YouTube or games, they may not stay
   focused on the task at hand.

.. danger::
   danger: Many kids have problems with screen time
   and if you leave them unattended with a
   screen and they have access to things
   like YouTube or games, they may not stay
   focused on the task at hand.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Usage:

   Usage/dependencies
   Usage/installation
   Usage/quick_summary
   Usage/tutorial

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Software:

   Software/description
   Software/paf_file
   Software/algorithms


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
