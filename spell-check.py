#!/usr/bin/env python3
#
# Copyright (c) 2018 Louis Langholtz https://github.com/louis-langholtz/pyspellcode
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

# This is a modified version of Langholtz original script.
# See: https://github.com/peterwicksstringfield/pyspellcode

import sys, subprocess, string, re, argparse, os

# Function to check that given argument names a file that exists.
# Function idea from https://stackoverflow.com/a/11541495/7410358
def extant_file(arg):
    return os.path.exists(arg)

def require_extant_file(arg):
    if not extant_file(arg):
        raise argparse.ArgumentTypeError("\"{0}\" does not exist".format(arg))
    return arg

# Setup some command line argument parsing...
# Note that convention for help text is to have first letter of string as
# lower-case and to not end with any punctuation.
parser = argparse.ArgumentParser(
    description="""
    Extract and spellcheck comments from provided C++ source.
    """)
parser.add_argument('-v', '--verbose',
    dest='verbose', action='store_true',
    help='gets more verbose to aid with diagnostics')
parser.add_argument('-I', '--include-dir',
    dest='includedirs', action='append', metavar='<dir>', nargs=1,
    help='adds directory to include search path, ignored if --use-tool is set')
parser.add_argument('-std=c99',
    dest='langstd', action='store_const', const='c99',
    help='selects the C99 language standard')
parser.add_argument('-std=c++11',
    dest='langstd', action='store_const', const='c++11',
    help='selects the C++11 language standard (default)')
parser.add_argument('-std=c++14',
    dest='langstd', action='store_const', const='c++14',
    help='selects the C++14 language standard')
parser.add_argument('-std=c++17',
    dest='langstd', action='store_const', const='c++17',
    help='selects the C++17 language standard')
parser.add_argument('--doxygen-only',
    dest='doxygen_only', action='store_true',
    help='skip normal comments (// and /* */), only check doxygen comments (/// and /** */)')
parser.add_argument('-e', '-Werror', '--error-exit',
    dest='nonzero_exit_on_misspellings', action='store_true',
    help='nonzero exit status for unrecognized words')
parser.add_argument('--show-file-progress',
    dest='show_file_progress', action='store_true',
    help='shows filenames and results even when no unrecognized words')
parser.add_argument('-p', '--personal-dict',
    dest='dict', metavar='<full-file-path>', nargs=1,
    help='specify the fullpath to a personal dictionary')
parser.add_argument('-c', '--collect',
    dest='collect', action='store_true',
    help='output deduplicated list of unrecognized words')
parser.add_argument('-x', '--extra-clang-arg',
    dest='extraClangArguments', action='append', default=list(),
    metavar='<extra-argument-to-clang>',
    help='extra argument for clang')
parser.add_argument('--use-tool',
    dest='use_tool', action='store_true',
    help='use specialized Clang Tool to extract comments')
parser.add_argument('--build-tool',
    dest='build_tool', action='store_true',
    help='build specialized Clang Tool and exit (no spellchecking); slow!')
parser.add_argument('--path-to-tool',
    dest='path_to_tool', action='store', default=".",
    metavar='<path-to-tool>',
    help='path to specialized build tool, default to CWD')
parser.add_argument('filenames',
    metavar='filename', type=require_extant_file, nargs='*',
    help='filename to inspect')

cmdlineargs = parser.parse_args()

langstd = 'c++11'
if cmdlineargs.langstd:
    langstd = cmdlineargs.langstd

files = cmdlineargs.filenames

# Need various clang options...
# -fsyntax-only tells clang to only examine syntax and to not generate object file
clangargs = ["clang++", "-Xclang", "-ast-dump", "-fsyntax-only", "-fno-color-diagnostics", "-Wno-error=deprecated"]
toolargs = [cmdlineargs.path_to_tool + "/extract-comments"]
clangargs.append('-std=' + langstd)
toolargs.append('--extra-arg=-std=' + langstd)
if not cmdlineargs.doxygen_only:
    clangargs.append('-fparse-all-comments')
    toolargs.append('--extra-arg=-fparse-all-comments')
if cmdlineargs.includedirs:
    for includedirs in cmdlineargs.includedirs:
        includedir = " ".join(includedirs)
        clangargs.append('-I' + includedir)
        toolargs.append('--extra-arg=-I' + includedir)
clangargs.extend(cmdlineargs.extraClangArguments)
toolargs.extend(map(lambda s: '--extra-arg=' + s, cmdlineargs.extraClangArguments))
if cmdlineargs.verbose:
    if cmdlineargs.use_tool:
        print("using specialized Clang Tool: {0}".format(toolargs))
    else:
        print("using built-in AST dumper: {0}".format(clangargs))

# Note: hunspell has issues with use of the apostrophe character.
# For details, see: https://github.com/marcoagpinto/aoo-mozilla-en-dict/issues/23
hunspellargs = ["hunspell", "-a"]
if cmdlineargs.dict:
    hunspellargs = hunspellargs + ["-p"] + cmdlineargs.dict
if cmdlineargs.verbose:
    print("using spelling tool: {0}".format(hunspellargs))

hunspellpipe = subprocess.Popen(hunspellargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)
hunspellpipe.stdout.readline() # read the first line from hunspell

def check_word(word):
    if re.search("^\W+$", word):
        return True
    if re.search("^\W", word):
        return False
    if not word:
        return True
    hunspellpipe.stdin.write((word + "\n").encode("utf-8"))
    hunspellpipe.stdin.flush()
    isokay = True
    for line in iter(hunspellpipe.stdout.readline, b''):
        line = line.decode("utf-8")
        if not line.rstrip("\n"):
            break
        if not line.startswith("*"):
            isokay = False
    return isokay

collectedUnrecognizedWords = set()

def check_file(path):
    argsneeded = clangargs + [path]
    # Note: Specifying bufsize=-1 hugely improves performance over its default!
    clangpipe = subprocess.Popen(argsneeded, bufsize=-1, stdout=subprocess.PIPE)
    astlinenum = 0
    foundnum = 0
    srclinenum = 0
    skipNextTextComment = False
    skipTillHTMLEndTagComment = False
    skipTillNextLinenum = False
    skipFirstWord = False
    skipTillNextDepth = 0
    misspellings = 0
    filenameShown = False
    if cmdlineargs.show_file_progress:
        print("file {0}:".format(path))
        filenameShown = True
    with clangpipe.stdout:
        for line in iter(clangpipe.stdout.readline, b''):
            line = line.decode("utf-8")
            line = line.rstrip()
            if cmdlineargs.verbose:
                print("checking: {0}".format(line))
            astlinenum += 1
            if (foundnum == 0):
                # We only want to spellcheck comments in the file the user
                # asked us to spellcheck, not all of its recursive includes, so
                # we throw out lines until we see one that refers to the file
                # we are interested in.
                pos = line.find(path)
                if (pos == -1):
                    continue
                # But this can happen: "TemplateArgument type
                # 'std::is_function<(lambda at
                # ../math/stan/math/rev/fun/inverse.hpp:47:29)>"
                if (line.find("(lambda at") == -1):
                    foundnum = astlinenum
            match = re.match("^(\W*)(\w.*)$", line)
            #print("lhs=\"{0}\" rhs=\"{1}\"".format(match.group(1), match.group(2)))
            depth = match.group(1)
            if (skipTillNextDepth and skipTillNextDepth < len(depth)):
                if cmdlineargs.verbose:
                    print("skipping: {0}".format(line))
                continue
            skipTillNextDepth = 0
            useful = match.group(2)
            fields = useful.split(" ", 2)
            if (len(fields) <= 2):
                # Shouldn't happen but apparently it did!
                continue
            nodetype = fields[0] # Like: FullComment
            nodehex  = fields[1] # Like: 0x10f24bb30
            nodedata = fields[2] # Like: <line:97:5, line:99:5>
            m = re.match("<([^>]*)>\s*(.*)", nodedata)
            if not m:
                continue
            locations = m.group(1).split(", ") # Ex: 'col:15, col:47'
            data = m.group(2) # Ex: 'Text=" Computes the AABB for the given body."'
            if (locations[0].startswith("line:")):
                linenum = locations[0].split(":")[1]
                #if (linenum < srclinenum):
                #    skipTillNextLinenum = True
                #    continue
                srclinenum = linenum
                skipTillNextLinenum = False
            if skipTillNextLinenum:
                continue
            if (nodetype == "HTMLEndTagComment"):
                skipTillHTMLEndTagComment = False
                continue
            if skipTillHTMLEndTagComment:
                continue
            if (nodetype == "HTMLStartTagComment"):
                skipTillHTMLEndTagComment = True
                continue
            if (nodetype == "BlockCommandComment"):
                if cmdlineargs.verbose:
                    print("found: {0}".format(useful))
                m = re.search("Name=\"([^\"]*)\"", useful)
                if not m:
                    continue
                cmdName = m.group(1)
                if (cmdName == "sa") or (cmdName == "see"):
                    skipTillNextDepth = len(depth)
                    continue
                if (cmdName == "throws"):
                    skipFirstWord = True
                    continue
                continue
            if (nodetype == "InlineCommandComment"):
                if not re.search("Name=\"image\"", useful):
                    continue
                skipNextTextComment = True
            if (nodetype != "TextComment"):
                continue
            if skipNextTextComment:
                skipNextTextComment = False
                continue
            if cmdlineargs.verbose:
                print(useful)
            if not (data.startswith("Text=\"")):
                continue
            #text = data.lstrip("Text=\"").rstrip("\"").lstrip(" ").lstrip(string.punctuation)
            text = data.lstrip("Text=\"").rstrip("\"").lstrip(" ").strip(string.punctuation)
            if not text:
                continue
            words = re.split("[\s]+", text) # Split on any space or dash char
            if cmdlineargs.verbose:
                print(words)
            unrecognizedwords = []
            for word in words:
                if skipFirstWord:
                    skipFirstWord = False
                    continue
                word = word.strip("\"\'").lstrip("(").rstrip(")").strip(string.punctuation)
                if not check_word(word):
                    unrecognizedwords.append(word)
                    misspellings += 1
            if not unrecognizedwords:
                continue
            if cmdlineargs.collect:
                collectedUnrecognizedWords.update(unrecognizedwords)
            elif not filenameShown:
                print("file {0}:".format(path))
                filenameShown = True
            if not cmdlineargs.collect or cmdlineargs.show_file_progress:
                print("  line #{0}, unrecognized words: {1}".format(srclinenum, unrecognizedwords))
    clangpipe.wait() # Blocks until clang exits
    if cmdlineargs.show_file_progress and misspellings == 0:
        print("  no unrecognized words")
    return misspellings

def check_file_with_tool(path):
    argsneeded = toolargs + [path] + ['--']
    toolpipe = subprocess.Popen(argsneeded, bufsize=-1, stdout=subprocess.PIPE)
    filenameShown = False
    if cmdlineargs.show_file_progress:
        print("file {0}:".format(path))
        filenameShown = True
    misspellings = 0
    with toolpipe.stdout:
        for comment in iter(toolpipe.stdout.readline, b''):
            comment = comment.decode("utf-8")
            comment = comment.rstrip()
            if cmdlineargs.verbose:
                print("checking: {0}".format(comment))
            words = re.split("[\s,.;?!:&_^()[\\]<>\"'{}=\\-+*/\\\\]+", comment)
            if cmdlineargs.verbose:
                print(words)
            unrecognizedwords = []
            for word in words:
                word = word.strip(string.punctuation)
                if not check_word(word):
                    unrecognizedwords.append(word)
                    misspellings += 1
            if not unrecognizedwords:
                continue
            if cmdlineargs.collect:
                collectedUnrecognizedWords.update(unrecognizedwords)
            elif not filenameShown:
                print("file {0}:".format(path))
                filenameShown = True
            if not cmdlineargs.collect or cmdlineargs.show_file_progress:
                print("  unrecognized words: {0}".format(unrecognizedwords))
    return misspellings

if cmdlineargs.build_tool:
    if not extant_file("./internals/build_clang_tool.sh"):
        print("Must be inside pyspellcode directory to build tool.")
        exit(1)
    try:
        subprocess.check_call("./internals/build_clang_tool.sh", shell=True)
        exit(0)
    except subprocess.CalledProcessError as e:
        print("Failed to build Clang Tool: {0}.".format(e))
        exit(1)

totalmisspellings = 0
for file in files:
    if cmdlineargs.use_tool:
        if not extant_file(cmdlineargs.path_to_tool + "/extract-comments"):
            print("Could not find Clang Tool, did you build it?")
            exit(1)
        totalmisspellings += check_file_with_tool(file)
    else:
        totalmisspellings += check_file(file)

if not files:
    print("No files selected.")

if cmdlineargs.collect:
    if collectedUnrecognizedWords:
        print("Found these unrecognized words ...")
        print("\n".join(list(collectedUnrecognizedWords)))
    else:
        print("All words recognized.")

hunspellpipe.stdin.close()
hunspellpipe.wait() # Blocks until hunspell exits

if ((totalmisspellings > 0) and cmdlineargs.nonzero_exit_on_misspellings):
    exit(1)

exit(0)
