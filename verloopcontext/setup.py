from setuptools import setup

setup(name="verloopcontext",
      version="0.0.5",
      description="Verloop context to pass headers and metadata around twirp",
      author="Piyush",
      author_email="piyush@verloop.io",
      licesnse='unlicense',
      packages=['verloopcontext'],
      install_requires=[
            'structlog',
            'protobuf'
      ],
      test_requires=[
      ],
      zip_safe=False)
