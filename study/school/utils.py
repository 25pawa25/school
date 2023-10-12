from __future__ import unicode_literals
from django.utils.text import slugify as django_slugify

import decimal
import json

def slugify(s):
    """
    Overriding django slugify that allows to use russian words as well.
    """
    alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
                'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
                'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ы': 'i', 'э': 'e',
                'ю': 'yu',
                'я': 'ya'}

    return django_slugify(''.join(alphabet.get(w, w) for w in s.lower()))


class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(Encoder, self).default(o)

