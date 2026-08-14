# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: SeedInfo for ftoBranchProc.spcs --- path-derived parameters
  for a branch in an FTO tree. The branch directory IS the parameter.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-u
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-u") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-u
#+end_org """
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
""" #+begin_org
* *[[elisp:(org-cycle)][| Proclamations |]]* :: Libre-Halaal Software --- Part Of BISOS ---  Poly-COMEEGA Format.
** This is Libre-Halaal Software. © Neda Communications, Inc. Subject to AGPL.
** It is part of BISOS (ByStar Internet Services OS)
** Best read and edited  with Blee in Poly-COMEEGA (Polymode Colaborative Org-Mode Enhance Emacs Generalized Authorship)
#+end_org """
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars |]]* :: Authors, version
** This File: /bisos/git/bxRepos/bisos-pip/fileObj/py3/bisos/fileObj/ftoBranch_seedInfo.py
** File True Name: /bisos/git/auth/bxRepos/bisos-pip/fileObj/py3/bisos/fileObj/ftoBranch_seedInfo.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inDev"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
if 'csInfo' not in globals(): import typing ; csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['loadAs'], }
csInfo['version'] = '202608130001'
csInfo['status']  = 'inDev'
csInfo['panel'] = 'ftoBranch_seedInfo-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: SeedInfo for the ftoBranch seed.
Provides =paramsFromPlantPath()= which resolves the branch directory
(the directory containing the planted =ftoBranchProc.spcs=), and a
singleton =FtoBranchSeedInfo= for optional control-info overrides
(=branchesList=, =leavesList=, =branchesExcludes=, =leavesExcludes=,
=branchesOrdered=, =leavesOrdered=).

The trivial-path case: for =ftoBranchProc.spcs=, the plant path itself
IS the parameter. No anchor-segment parsing is needed --- the branch
directory is =pathlib.Path(plantOfThisSeed).resolve().parent=.

** Status: In development
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]

#+end_org """
####+END:

####+BEGIN: b:py3:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]] || [[elisp:(python-check (format "/bisos/pipx/bin/pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "/bisos/pipx/bin/pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "/bisos/pipx/bin/pycodestyle %s" (bx:buf-fname))))][pycodestyle]] | [[elisp:(python-check (format "/bisos/pipx/bin/flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "/bisos/pipx/bin/pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

import typing
import pathlib
from dataclasses import dataclass, field

from bisos.csSeed import seedsLib


###############################################################################
# BranchParams --- path-derived parameters for a planted branch
###############################################################################

@dataclass
class BranchParams:
    """Parameters derived from a planted ftoBranchProc.spcs's location."""
    branchPath: pathlib.Path = field(default_factory=pathlib.Path)
    plantPath: str = ""


###############################################################################
# WalkExampleSpec --- a leaf-seed-owned walk example
###############################################################################

@dataclass
class WalkExampleSpec:
    """One example of a walk invocation that makes sense at the branch's leaves.

    Populated by a leaf-side seed (e.g. =bisos.dockerProc.containerProc_seedInfo=)
    and passed by the branch's =.spcs= into =ftoBranch_seedInfo.setup(leafExamples=...)=.
    The branch-side seed's examples menu renders each spec as a proper
    =cs.examples.cmndEnter= line targeting =fto_forwardToLeaves= (Mode 1) or
    =fto_walkRunExternal= (Mode 2).

    Fields:
    - =cmndName=: for Mode 1, the leaf-side Cmnd verb to forward. For Mode 2,
      the external cmnd name (=argv[0]=).
    - =pars=: dict of param-name → value forwarded to the leaf Cmnd (Mode 1)
      or ignored (Mode 2 --- args go in =args=).
    - =args=: for Mode 2, the args string appended after =cmndName=. Ignored
      for Mode 1 (the leaf's own Cmnd handles its args).
    - =comment=: one-line description shown after the invocation in the menu.
    - =mode=: 'forwardToLeaves' (Mode 1, default) or 'walkRunExternal' (Mode 2).
    - =tags=: free-form set of tags (e.g. =docker=, =podman=, =read-only=,
      =destructive=) for future filtering.
    """
    cmndName: str = ""
    pars:    dict = field(default_factory=dict)
    args:    str  = ""
    comment: str  = ""
    mode:    str  = "forwardToLeaves"   # or 'walkRunExternal'
    tags:    frozenset = field(default_factory=frozenset)


###############################################################################
# paramsFromPlantPath --- pure function, no side effects
###############################################################################

def paramsFromPlantPath(
        plantPath: typing.Optional[str] = None,
) -> BranchParams:
    """Derive BranchParams from the planted .spcs's location.

    Trivial-path case: the plant path itself IS the parameter. The
    branch is the directory containing the planted ftoBranchProc.spcs.

    Raises ValueError if =plantOfThisSeed= is not set (i.e. running
    outside of a plant context).
    """
    if plantPath is None:
        plantPath = seedsLib.seededCsxuInfo.plantOfThisSeed

    if plantPath is None:
        raise ValueError(
            "plantPath is None and plantOfThisSeed is not set --- "
            "ftoBranchProc.spcs must be invoked as a planted CS"
        )

    resolvedFile = pathlib.Path(plantPath).resolve()
    if resolvedFile.is_file():
        branchDir = resolvedFile.parent
    else:
        branchDir = resolvedFile

    return BranchParams(
        branchPath=branchDir,
        plantPath=str(resolvedFile),
    )


###############################################################################
# FtoBranchSeedInfo --- singleton for control-info overrides
###############################################################################

@dataclass
class FtoBranchSeedInfo:
    """Optional control-info overrides declared by a planted .spcs.

    Autodiscover applies when a field is None. Set these via =setup()=
    from a .spcs file only when the branch needs explicit membership
    control.
    """
    branchesList:     typing.Optional[list[str]] = None
    branchesExcludes: typing.Optional[list[str]] = None
    branchesOrdered:  typing.Optional[list[str]] = None
    leavesList:       typing.Optional[list[str]] = None
    leavesExcludes:   typing.Optional[list[str]] = None
    leavesOrdered:    typing.Optional[list[str]] = None
    examplesFuncsList: typing.Optional[list[typing.Callable]] = None
    leafExamples:      typing.Optional[list['WalkExampleSpec']] = None
    # Filenames whose presence in a directory identifies it as a leaf.
    # Populated by the branch's .spcs, typically from the domain seed's
    # leafProcessorNames() function (e.g.
    # containerProc_seedInfo.leafProcessorNames() → ['dockerProc.spcs',
    # 'podmanProc.spcs']). When set, the walker detects leaves
    # definitionally --- no per-leaf _tree_=leaf marker needed.
    leafProcessors:    typing.Optional[list[str]] = None

    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


ftoBranchSeedInfo = FtoBranchSeedInfo()   # the singleton used by .spcs files


###############################################################################
# setup --- called by a .spcs to override autodiscover
###############################################################################

def setup(
        branchesList:      typing.Optional[list[str]] = None,
        branchesExcludes:  typing.Optional[list[str]] = None,
        branchesOrdered:   typing.Optional[list[str]] = None,
        leavesList:        typing.Optional[list[str]] = None,
        leavesExcludes:    typing.Optional[list[str]] = None,
        leavesOrdered:     typing.Optional[list[str]] = None,
        examplesFuncsList: typing.Optional[list[typing.Callable]] = None,
        leafExamples:      typing.Optional[list['WalkExampleSpec']] = None,
        leafProcessors:    typing.Optional[list[str]] = None,
) -> None:
    """Populate the FtoBranchSeedInfo singleton from a .spcs file.

    Any argument left at None keeps the singleton's existing value
    (default None --- autodiscover).
    """
    if branchesList      is not None: ftoBranchSeedInfo.branchesList      = branchesList
    if branchesExcludes  is not None: ftoBranchSeedInfo.branchesExcludes  = branchesExcludes
    if branchesOrdered   is not None: ftoBranchSeedInfo.branchesOrdered   = branchesOrdered
    if leavesList        is not None: ftoBranchSeedInfo.leavesList        = leavesList
    if leavesExcludes    is not None: ftoBranchSeedInfo.leavesExcludes    = leavesExcludes
    if leavesOrdered     is not None: ftoBranchSeedInfo.leavesOrdered     = leavesOrdered
    if examplesFuncsList is not None: ftoBranchSeedInfo.examplesFuncsList = examplesFuncsList
    if leafExamples      is not None: ftoBranchSeedInfo.leafExamples      = leafExamples
    if leafProcessors    is not None: ftoBranchSeedInfo.leafProcessors    = leafProcessors


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
