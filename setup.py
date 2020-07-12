from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='scrab',
    description='Fast and easy to use scraper for the content-centered web pages, e.g. blog posts, news, etc.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.0.3',
    keywords='scrab scraper crawler extractor converter web content html text',
    url='https://github.com/gindex/scrab',
    author='Yevgen Pikus',
    author_email='yevgen.pikus@gmail.com',
    license='MIT',
    install_requires=['click', 'requests', 'lxml'],
    tests_require=['pytest', 'mypy'],
    packages=find_packages(exclude=["tests", "tests.*", "tests/*"]),
    scripts=['scrab/scrab'],
    python_requires='>=3.8',
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
        "Topic :: Text Processing",
    ],
)
