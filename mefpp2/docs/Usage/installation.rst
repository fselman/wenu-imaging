Installation Instructions
+++++++++++++++++++++++++

The program has to be compiled in three sequential stages. Although the main
directory created after un-tarring the file is called mefpp, it really is the top
directory of eclipse-5.5.0. Inside this directory the mef processing engine
can be found in ins/mef. The building and compilation of the software
is done with the following steps:


    #. Download and compile qfits5 
        * cd into ${qfits5} and run ./configure –prefix=${MEFPP}
        * then type: make;
        * when the compilation ends, type: make install
    #. Download and compile mefpp
        * cd ${MEFPP}
        * run ./configure –prefix=${MEFPP}
        * run make;
        * run make -B install
        * run: e_setup

.. warning::
    At runtime one could get an error about maximum number of pointer allocated. If that
    happens I suggest to edit the file xmemory.c en qfits/src and change the line:

    .. code-block:: C++

        #define XMEMORY_MAXPTRS 200000

    to a larger value (multiple of 2).
