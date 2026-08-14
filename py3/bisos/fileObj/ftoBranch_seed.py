# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: atexit registration for ftoBranch-seed.cs (ftoBranchProc.spcs)
#+end_org """

if 'csInfo' not in globals(): import typing ; csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['loadAs'], }
csInfo['version'] = '202608130001'
csInfo['status']  = 'inDev'

import atexit

from bisos.csSeed import seedsLib

seedCSXU = 'ftoBranch-seed.cs'


@atexit.register
def atexit_plantWithWhich(
        seedName: str = seedCSXU,
) -> None:
    seedsLib.plantWithWhich(seedName)


### local variables:
### no-byte-compile: t
### end:
