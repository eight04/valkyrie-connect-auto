valkyrie-connect-auto
=====================

Automation for valkyrie connect.

Installation
------------

To use drop potion, you have to install tesseract:
https://github.com/UB-Mannheim/tesseract/wiki

Then make sure you have `tesseract` command in your PATH:
```bash
$ tesseract --version
```

Install valkyrie-connect-auto:
```bash
$ pip install https://github.com/eight04/valkyrie-connect-auto/archive/refs/heads/master.zip
```

Usage
---------

Start a normal event battle and run:

```bash
$ valkyrie-connect-auto event --loop 20 --double-drop-potion 10
```

Start a dragon raid and run:

```bash
$ valkyrie-connect-auto dragon --loop 20
```

Changelog
---------

* 0.1.0 (Jun 12, 2024)

	- First release.
