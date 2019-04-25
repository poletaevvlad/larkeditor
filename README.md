# lark-editor

`lark-editor` is a GTK-based development tool for creating and editing
context-free grammar files used by the [Lark parsing library](https://github.com/lark-parser/lark/).
It allows users to see how their rules affect the abstract syntax tree
generation without the need to terminate and rerun their applications.

Features of `lark-editor` include:

* syntax and error highlighting;
* autocompletion of rule and terminal names;
* automatic generation of an AST based on user-defined grammar and text;
* an ability to configure the parser (Earley, LARL or CYK) and starting rule;
* saving and loading grammar and text to/from a file.

There are some limitations of this software. As it has been developed as a tool
to be used during the development of another project, I have not written any
automatic tests due to time constraints. The dark version of the UI has not been
implemented yet.

![](https://raw.githubusercontent.com/poletaevvlad/larkeditor/master/screenshots/arithmetic.png)

## Installation

`lark-editor` requires Python 3.6 or newer. Older versions of the interpreter
are not supported.

`lark-editor` has some dependencies that are not as straightforward to install
as one might hope.  First of all, it depends on GTK and its python bindings ---
`pygobject`. Fortunately, it can be installed via package managers of some
popular Linux distributions. For the instructions for installing `pygobject` and
its transient dependencies, please refer to the
[installation guide](https://pygobject.readthedocs.io/en/latest/getting_started.html).

Another dependency is [GtkSourceView](https://wiki.gnome.org/Projects/GtkSourceView).
You can install it from the [tarball](https://download.gnome.org/sources/gtksourceview/)
or via your system's package manager.

Although it is theoretically possible to run `lark-editor` on Windows OS, it has
not been tested.

After native dependencies are resolved, you may install `lark-editor` globally
or in a python virtual environment by cloning this repository and running
`setup.py install`:

```bash
git clone https://github.com/poletaevvlad/larkeditor
cd larkeditor
python3 setup.py install
```

**Note**: If you install `lark-editor` into a virtual environment, you need to
first install `pygobject` using pip. It will not work without native libraries.

```bash
pip install pygobject
```

## Usage

After installation, you may run `lark-editor` by using a 'gui_script' created
by `setup.py` or by running the module `larkeditor`. Either one of the following
options should work:

```bash
lark-editor [filename]
```

or
```bash
python3 -m larkeditor
```

![](https://raw.githubusercontent.com/poletaevvlad/larkeditor/master/screenshots/python-error.png)

## License

This application is licensed under BSD 2-clause license. You can find the text
of the license in the [`LICENSE`](https://github.com/poletaevvlad/larkeditor/blob/master/LICENSE) file.

Several third-party open source licenses are used. The licensing information can
be found in [`LICENSE-3RD-PARTY`](https://github.com/poletaevvlad/larkeditor/blob/master/LICENSE-3RD-PARTY) file.