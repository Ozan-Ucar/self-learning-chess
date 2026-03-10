from setuptools import setup, find_packages

setup(
    name="vanguard_chess",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
    ],
    author="ou1534s",
    description="Bitboard-based Chess Engine",
)
