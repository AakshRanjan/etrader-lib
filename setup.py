from setuptools import setup, find_packages

# Read the contents of your README file.
with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="etrader-lib",
    author="Aaksh Ranjan",
    version="0.1.0",
    package_dir={"": "package"},
    packages=find_packages(),
    description="A simple package to trade on the stock market using the ETrade API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AakshRanjan/etrader-lib",
    license="MIT",
    classifiers=[
        "license :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests==2.31.0"],
    python_requires=">=3.10",
)
