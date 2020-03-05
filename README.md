# Fork
This version of pyspellcode has been hacked up to be used on the Stan Math library. Many of the improvements are not Stan specific, consider forking off the non_stan_specific_changes branch.

# pyspellcode
Python script for using `clang` and `hunspell` for spell checking source code comments.

pyspellcode implements two strategies for extracting comments:
1. (default) Use Clang's built-in AST dump tool. This will traverse all included files, including third party libraries, and it will only extract comments that are attached to declarations.
2. Use a specialized Clang tool. This will traverse only the indicated files, skipping includes, and it will extract all comments. It is necessary to build the tool first, which takes a while. It is likely that updates to clang will break the build process.

# Usage

0. (install clang and hunspell)
1. git clone
2. pyspellcode/spell-check.py example/example1.cpp ...
3. (optionally ...)
4. pyspellcode/spell-check.py --build-tool
5. (wait for a long time)
6. pyspellcode/spell-check.py --use-tool example/example1.cpp ...

For the most up-to-date command line argument usage, run the script with the `--help` flag (`-h` for short). For example:

```
usage: spell-check.py [-h] [-v] [-I <dir>] [-std=c99] [-std=c++11]
                      [-std=c++14] [-std=c++17] [--doxygen-only] [-e]
                      [--show-file-progress] [-p <full-file-path>] [-c]
                      [-x <extra-argument-to-clang>] [--use-tool]
                      [--build-tool]
                      [filename [filename ...]]

Extract and spellcheck comments from provided C++ source.

positional arguments:
  filename              filename to inspect

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         gets more verbose to aid with diagnostics
  -I <dir>, --include-dir <dir>
                        adds directory to include search path, ignored if
                        --use-tool is set
  -std=c99              selects the C99 language standard
  -std=c++11            selects the C++11 language standard (default)
  -std=c++14            selects the C++14 language standard
  -std=c++17            selects the C++17 language standard
  --doxygen-only        skip normal comments (// and /* */), only check
                        doxygen comments (/// and /** */)
  -e, -Werror, --error-exit
                        nonzero exit status for unrecognized words
  --show-file-progress  shows filenames and results even when no unrecognized
                        words
  -p <full-file-path>, --personal-dict <full-file-path>
                        specify the fullpath to a personal dictionary
  -c, --collect         output deduplicated list of unrecognized words
  -x <extra-argument-to-clang>, --extra-clang-arg <extra-argument-to-clang>
                        extra argument for clang
  --use-tool            use specialized Clang Tool to extract comments
  --build-tool          build specialized Clang Tool; slow!
```

# Additional

Thanks to Louis Langholtz for the original implementation.
https://github.com/louis-langholtz/pyspellcode

Thanks to Daniel Beard for the clang tool code.
https://gist.github.com/daniel-beard?page=1

(... and of course to the developers of Clang and hunspell.)

This fork of pyspellcode incorporates a small amount of modified Clang code.
