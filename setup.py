from Cython.Build import cythonize
from setuptools import Extension, find_packages, setup

with open("README.md") as f:
    long_description = f.read()

with open("htmlgenerator/__init__.pyx") as f:
    # magic n stuff
    version = (
        [i for i in f.readlines() if "__version__" in i][-1]
        .split("=", 1)[1]
        .strip()
        .strip('"')
    )

extensions = [
    Extension("htmlgenerator", ["htmlgenerator/__init__.pyx"]),
    Extension("htmlgenerator.base", ["htmlgenerator/base.pyx"]),
    Extension("htmlgenerator.htmltags", ["htmlgenerator/htmltags.pyx"]),
    Extension("htmlgenerator.lazy", ["htmlgenerator/lazy.pyx"]),
    Extension("htmlgenerator.safestring", ["htmlgenerator/safestring.pyx"]),
]


setup(
    name="htmlgenerator",
    description="Declarative HTML templating system with lazy rendering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/basxsoftwareassociation/htmlgenerator",
    author="basx Software Association",
    author_email="sam@basx.dev",
    version=version,
    license="New BSD License",
    packages=find_packages(),
    ext_modules=cythonize(extensions, annotate=True, language_level=3),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
