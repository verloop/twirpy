from setuptools import setup

setup(name="vtwirp",
      version="0.0.1",
      description="Verloop twirp server",
      author="Piyush",
      author_email="piyush@verloop.io",
      licesnse='unlicense',
      packages=['vtwirp'],
      install_requires=[
            'ujson',
            'requests'
      ],
      test_requires=[
      ],
      zip_safe=False)
