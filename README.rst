AstroPoP
========

|GHAction Status| |Codecov Status| |RTD Status| |CODACY|

The (non) famous ASTROnomical POlarimetry and Photometry pipeline. Developed for work with IAGPOL polarimeter at Observatório Pico dos Dias (Brazil), but suitable to be used in other image polarimeters around the world.

Features
^^^^^^^^

This software is intended to provide a full pipeline to reduce raw polarimetry and photometry data taken with common CCD telescope cameras. It can do:

- Create calibrate frames;

- Calibrate images using bias/flat/dark frames;

- Gain correction and in-processing image binnig;

- Cosmic ray extraction (astroscrappy);

- Align image sets;

- Aperture and (planned) PSF photometry;

- Calcite polarimeters;

  - Automatic pairs of stars identification;

- Automatic photometry calibration using online catalogs.


Dependencies
^^^^^^^^^^^^

Some of astropop dependencies (numpy, astropy, scipy, astroscrappy) need gcc to get build. Make sure gcc is installed properly in your system.

Bellow we list all the necessary dependencies for the good working of the code. Note that this can be changed with the time.

- astroalign;

- astropy >= 4.3;

- astroquery;

- astroscrappy;

- numpy >= 1.17;

- scikit-image;

- scikit-learn;

- scipy;

- sep.

Installation
^^^^^^^^^^^^
Astropop can be downloaded from https://github.com/sparc4-dev/astropop. For this, type in the terminal:

.. code-block::

    git clone https://github.com/sparc4-dev/astropop

To install Astropop, you should go to the directory where Astropop was cloned, open the terminal in the Astropop directory and follow one of the options bellow:

1 – Install using pip:

.. code-block::

    pip install -U .

2 – Or, without the pip packet control:

.. code-block::

    python setup.py install

3 – Install using anaconda:

If you do not have anaconda, please visit https://www.anaconda.com/.
Once the anaconda is installed you can create an Astropop enviroment using:

.. code-block::

    conda create -n <environment name> -c conda-forge python=3.9 astroalign astropy astroquery astroscrappy matplotlib numpy pyyaml reproject scikit-image scikit-learn scipy sep

Citating
^^^^^^^^

|ADS|  |PASP|  |arXiv|  |ASCL|

An article was published in `Publications of the Astronomical Society of the Pacific, vol.131, n.996, pp.024501 <https://iopscience.iop.org/article/10.1088/1538-3873/aaecc2>`_,
which is the main reference to this work. If you do not have access to PASP, the preprint was uploaded to `arXiv:1811.01408 <https://arxiv.org/abs/1811.01408>`_.

Also, for latex citation, you can use the following BibTex:

.. code-block::

    @article{Campagnolo_2018,
    	doi = {10.1088/1538-3873/aaecc2},
	    url = {https://doi.org/10.1088%2F1538-3873%2Faaecc2},
	    year = 2018,
	    month = {dec},
	    publisher = {{IOP} Publishing},
	    volume = {131},
	    number = {996},
	    pages = {024501},
	    author = {Julio Cesar Neves Campagnolo},
	    title = {{ASTROPOP}: the {ASTROnomical} {POlarimetry} and Photometry Pipeline},
	    journal = {Publications of the Astronomical Society of the Pacific},
    }

Documentation
^^^^^^^^^^^^^

Documentation (not complete yet) can be found at `astropop.readthedocs.io <https://astropop.readthedocs.io>`_

.. |GHAction Status| image:: https://github.com/sparc4-dev/astropop/actions/workflows/unit-tests.yml/badge.svg
    :target: https://github.com/sparc4-dev/astropop/actions
    :alt: Astropop's Github CI Status

.. |Codecov Status| image:: https://codecov.io/gh/sparc4-dev/astropop/branch/main/graph/badge.svg?token=tzrOfWMhUb
    :target: https://codecov.io/gh/sparc4-dev/astropop
    :alt: Astropop's Codecov Coverage Status

.. |RTD Status| image:: https://readthedocs.org/projects/astropop/badge/?version=latest
    :target: https://astropop.readthedocs.io/en/latest/?badge=latest
    :alt: Astropop's Documentation Status

.. |Powered by Astropy|  image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org/
    :alt: Powered by AstroPy

.. |ADS|  image:: http://img.shields.io/badge/ADS-2019PASP..131b4501N-blue.svg?style=flat
    :target: https://ui.adsabs.harvard.edu/abs/2019PASP..131b4501N/abstract
    :alt: ADS Reference

.. |PASP| image:: http://img.shields.io/badge/PASP-pp.024501-blue.svg?style=flat
    :target: https://iopscience.iop.org/article/10.1088/1538-3873/aaecc2
    :alt: Publications of the Astronomy Society of the Pacific

.. |arXiv|  image:: http://img.shields.io/badge/arXiv-1811.01408-red.svg?style=flat
    :target: https://arxiv.org/abs/1811.01408
    :alt: arXiv preprint

.. |ASCL|  image:: https://img.shields.io/badge/ascl-1805.024-blue.svg?colorB=262255
    :target: http://ascl.net/1805.024
    :alt: ASCL register

.. |CODACY|  image:: https://app.codacy.com/project/badge/Grade/ab9d4647935d4b33aee0544b6957d7a7
    :target: https://www.codacy.com/gh/sparc4-dev/astropop/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sparc4-dev/astropop&amp;utm_campaign=Badge_Grade
