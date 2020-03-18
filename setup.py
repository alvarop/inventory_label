import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="inventory_label",
    version="0.0.1",
    author="Alvaro Prieto",
    author_email="source@alvaroprieto.com",
    description="Inventory label generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alvarop/inventory_label",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Pillow',
        'pylibdmtx'
    ],
    python_requires='>=3.6',
)