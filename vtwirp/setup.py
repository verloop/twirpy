from setuptools import setup

setup(name="vtwirp",
      version="0.0.3",
      description="Verloop twirp server",
      author="Piyush",
      author_email="piyush@verloop.io",
      licesnse='unlicense',
      packages=['vtwirp','vtwirp.hooks'],
      install_requires=[
            'ujson',
            'requests',
            'verloopcontext'
      ],
      test_requires=[
      ],
      zip_safe=False)
