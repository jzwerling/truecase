# TrueCase

Work in progress, branched off of [truecase](https://github.com/daltonfury42/truecase) by Dalton Fury.
Most tools I found, including truecase, process non-whitespace tokens, and then do something like ' '.join(tokens) to reassemble the sentence or document.  I had data with a lot of weird  whitespace that i needed to preserve, so I made some small changes to the tokenization part of the code, left pretty much everything else intact.
