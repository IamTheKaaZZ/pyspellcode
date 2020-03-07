#!/bin/bash
# Thanks F. Hauri!
# https://stackoverflow.com/a/13805282
function popline() {
    sed -e \$$'{w/dev/stdout\n;d}' -i~ $1
}
export word=$(popline wordlist)
echo $word
emacsclient $(ag -l "$word" stan/math) $(ag -l "$word" test/)
