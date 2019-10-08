from setuptools import setup, find_packages

setup(
    name='stratatools',
    version='3.0',
    description='A library to interact with Stratasys cartridge material.',
    #long_description=long_description,
    url='https://github.com/bvanheu/stratatools',
    author='benjamin vanheuverzwijn',
    author_email='bvanheu@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='stratasys 3dprinting',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'pycryptodome',
        'pyserial',
        'protobuf',
        'pyudev'
    ],
    extras_require={
        'testing': ['pytest'],
    },
    test_suite='stratatools',
    entry_points={
        'console_scripts': [
            'stratatools=stratatools.console_app:main',
            'stratatools_bp_read=stratatools.helper.bp_read:main',
            'stratatools_bp_write=stratatools.helper.bp_write:main',
            'stratatools_rpi_daemon=stratatools.helper.rpi_daemon:main',
        ],
    },
)
