###
# Copyright (c) 2002, Jeremiah Fincher
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import operator
import re

def any(p, seq):
    """Returns true if any element in seq satisfies predicate p."""
    return reduce (operator.or_, [p(i) for i in seq])

consonants = 'bcdfghjklmnpqrstvwxz'
_pluralizeRegex = re.compile('[%s]y$' % consonants)
def pluralize(s, i=2):
    """Returns the plural of s based on its number i.  Put any exceptions to
    the general English rule of appending 's' in the plurals dictionary.
    """
    if i == 1:
        return s
    else:
        # Words ending with 'ch', 'sh' or 'ss' such as 'punch(es)', 'fish(es)
        # and miss(es)
        if any (s.endswith, ['ch', 'sh', 'ss']):
            return s+'es'
        # Words ending with a consonant followed by a 'y' such as
        # 'try (tries)' or 'spy (spies)'
        elif re.search(_pluralizeRegex, s):
            return s[:-1] + 'ies'
        # In all other cases, we simply add an 's' to the base word
        else:
            return s+'s'
