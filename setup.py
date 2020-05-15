from setuptools import setup

setup(name="twirp",
      version="0.0.1",
      description="Twirp server and client libs",
      licesnse='unlicense',
      packages=['twirp'],
      install_requires=[
            'requests',
            'structlog',
            'protobuf'
      ],
      test_requires=[
      ],
      zip_safe=False)
