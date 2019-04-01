from setuptools import setup, find_packages

setup(
    name='larkeditor',
    version='0.1.3',
    packages=find_packages(),
    include_package_data=True,

    url='https://github.com/poletaevvlad/larkeditor',
    license='BSD 2-Clause License',
    author='Vlad Poletaev',
    author_email='poletaev.vladislav@gmail.com',
    description='An editor for EBNF grammars, used by Lark – parsing library for Python',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development"
    ],

    entry_points={
        "gui_scripts": [
            "lark-editor = larkeditor.__main__:main"
        ]
    },

    install_requires=[
        "lark-parser"
    ]
)
