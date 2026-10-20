Step-by-step guide
++++++++++++++++++
.. _stepbysteptutorial:

It will be assumed that the user have several nights of data in some directory that 
will be called `rawdir`. Let us assume that the data are store at `/data/raw`: Our rawdir can be
any of

    - /data/raw/2005-07-03
    - /data/raw/2005-07-04
    - /data/raw/2005-07-05

It will be also assumed that the data processing will be carried out in the workdir.
In what follow it will be assumed that  the commands will be issued from a
terminal in workdir.

Setting up the processing environment
=====================================

Copying PAF file
----------------

Copy the mefpp.paf file into the workdir. 

.. code-block:: bash 

   $ cp wfi.paf <workdir>/mefpp.paf

.. warning:: Note that if this file is not present, the program will crash
   with some criptic message suh as “Segmentation Fault” or “Bus error.” 
   It should be called mefpp.paf. It contains all the parameters for the 
   appropriate instrument.
