from itertools import cycle, islice
from random import random
import unicodedata
import re

def gen_spin(s):
    arr = s.split(' ')
    spins = {}
    for t in range(1,len(arr)+1):
        for i in range(len(arr)):
            before = " ".join(arr[:i])
            current = " ".join(arr[i:i+t])
            after = " ".join(arr[i+t:])
            if current not in spins:
                spins[current] = []
            
            r=[]
            if len(before)>0:
                r.append(before)
            if len(after)>0:
                r.append(after)
            spins[current].append(r)
            # spins.append(spin)
    return spins


def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

proxy_url = [line.strip() for line in open('proxies_url.txt').readlines()]
fetch_url = [line.strip() for line in open('fetch_url.txt').readlines()]
