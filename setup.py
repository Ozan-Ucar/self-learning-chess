from setuptools import setup, find_packages

setup(
    name="self-learning-chess",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
    ],
    author="ou1534s",
    description="A self-learning chess engine using bitboards and reinforcement learning.",
)
