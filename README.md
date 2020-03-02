# Fork
This version of pyspellcode has been hacked up to be used on the Stan Math library.

# pyspellcode
Python script for using `clang` and `hunspell` for spell checking source code comments.

This script parses the [AST dump](http://clang.llvm.org/docs/IntroductionToTheClangAST.html) output from `clang` and runs words found in comment nodes through `hunspell`. It's not perfect, but it's completely IDE independent. It just needs `clang` and `hunspell`. So it should be usable in continuous integration environments like [Travis CI](https://travis-ci.org).

The script accepts command line arguments to fine tune what it does. These arguments are similar to what `clang` and `hunspell` use for doing things like setting which programming language standard to use or adding a personal dictionary file. Note that by default, not all comments are spell checked. Only documentation comments are checked. To check all comments (including regular, non-documentation comments), use the `--all-comments` flag (`-a` for short).

For the most up-to-date command line argument usage, run the script with the `--help` flag (`-h` for short). For example:

```
$ ./spell-check.py --help
