# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Unit= exposing the =bisos.fileObj.fto= walker + node
  manipulation as PyCS Cmnds. Consumed by =ftoBranchProc.spcs= (branch-side
  spread-planted CS) --- these Cmnds are what a branch invokes locally when
  a =-i fto_<name>= arrives; anything else is forwarded via =treeRecurse=.
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
** This File: /bxRepos/bisos-pip/fileObj/py3/bisos/fileObj/fto_csu.py
** File True Name: /bisos/git/auth/bxRepos/bisos-pip/fileObj/py3/bisos/fileObj/fto_csu.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inDev"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
if 'csInfo' not in globals(): import typing ; csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['fto_csu'], }
csInfo['version'] = '202608120001'
csInfo['status']  = 'inDev'
csInfo['panel'] = 'fto_csu-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]]
Two Cmnd groups exposed here:

** Introspection Cmnds (=fto_nodeInfo=, =fto_effectiveBranches=, ...)
Read the target directory and report --- do not modify. When invoked at
a branch =.spcs=, they run *locally* against that branch (not forwarded
to leaves).

** Creation Cmnds (=fto_branchCreate=, =fto_leafCreate=, ...)
Write marker files (=_tree_= / =_treeProc_= / =_objectType_=) at the
target directory. One-shot setup operations.

** Status: inDev (Stage 1 scaffolding)
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_    CsFrmWrk *Imports* =Based on Classification=cs-u=
#+end_org """
from bisos import b  # noqa: E402
from bisos.b import cs
from bisos.b import b_io

import collections
####+END:

import pathlib
import typing

from bisos.fileObj import fto


###############################################################################
# commonParamsSpecify --- register CS params used by the Cmnds below.
# Without this, --path / --treeProc / --objectType are rejected by argparse
# even though the Cmnd classes declare them in cmndParamsOptional.
###############################################################################

def commonParamsSpecify(
        csParams: cs.param.CmndParamDict,
) -> None:
    csParams.parDictAdd(
        parName='path',
        parDescription="Target directory (defaults to cwd).",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        argparseShortOpt=None,
        argparseLongOpt='--path',
    )
    csParams.parDictAdd(
        parName='treeProc',
        parDescription="Value to write into =_treeProc_= (name of processor executable).",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        argparseShortOpt=None,
        argparseLongOpt='--treeProc',
    )
    csParams.parDictAdd(
        parName='objectType',
        parDescription="Value to write into =_objectType_= (type metadata).",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        argparseShortOpt=None,
        argparseLongOpt='--objectType',
    )


###############################################################################
# Helpers
###############################################################################

def _targetPath(pathParam: typing.Optional[str]) -> pathlib.Path:
    """Resolve the target directory from the --path param, defaulting to cwd."""
    if pathParam:
        return pathlib.Path(pathParam).resolve()
    return pathlib.Path.cwd()


###############################################################################
# examples_csu
###############################################################################

def examples_csu() -> None:
    """ #+begin_org
** [[elisp:(org-cycle)][| *DocStr* |]] Examples menu for the fto_* Cmnd surface.
    #+end_org """

    od = collections.OrderedDict
    cmnd = cs.examples.cmndEnter

    cs.examples.menuChapter('*bisos.fileObj.fto --- Node Introspection*')

    cs.examples.menuSection('Introspection (read-only)')
    cmnd('fto_nodeInfo',           comment="# print _tree_ / _treeProc_ / _objectType_ at cwd")
    cmnd('fto_branchPredicate',    comment="# exit 0 if cwd is a branch")
    cmnd('fto_leafPredicate',      comment="# exit 0 if cwd is a leaf")
    cmnd('fto_effectiveBranches',  comment="# list child branches beneath cwd")
    cmnd('fto_effectiveLeaves',    comment="# list child leaves beneath cwd")
    cmnd('fto_treeList',           comment="# recursive list of every node beneath cwd (dry run)")

    cs.examples.menuChapter('*bisos.fileObj.fto --- Node Creation*')

    cs.examples.menuSection('Creation (writes marker files)')
    cmnd('fto_branchCreate',       comment="# mark cwd as a branch")
    cmnd('fto_branchCreate',
         pars=od([('treeProc', 'ftoBranchProc.spcs'), ('objectType', 'fto.branch')]),
         comment="# with _treeProc_ + _objectType_")
    cmnd('fto_leafCreate',         comment="# mark cwd as a leaf")
    cmnd('fto_leafCreate',
         pars=od([('treeProc', 'containerProc-seed.cs'), ('objectType', 'fto.leaf')]),
         comment="# with a leaf processor named")
    cmnd('fto_auxBranchCreate',    comment="# traverse but skip processing")
    cmnd('fto_auxLeafCreate',      comment="# skip application, no error")
    cmnd('fto_ignoreCreate',       comment="# skip this and everything below")


###############################################################################
# ============================ Introspection ==================================
###############################################################################

class fto_nodeInfo(cs.Cmnd):
    """Print =_tree_= / =_treeProc_= / =_objectType_= for a node."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        callParamsDict = {'path': path}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)

        target = _targetPath(path)
        obj = fto.FILE_TreeObject(target)
        nt = obj.nodeType()
        tp = obj.treeProc()
        ot = obj.objectType()

        b_io.ann.note(f"path:       {target}")
        b_io.ann.note(f"nodeType:   {nt.name if nt else '(no _tree_ marker)'}")
        b_io.ann.note(f"treeProc:   {tp if tp else '(none)'}")
        b_io.ann.note(f"objectType: {ot if ot else '(none)'}")

        return cmndOutcome.set(
            opError=b.op.OpError.Success,
            opResults={'nodeType': nt.name if nt else None, 'treeProc': tp, 'objectType': ot},
        )


class fto_branchPredicate(cs.Cmnd):
    """Exit 0 (success) if target is a branch; failure otherwise."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        callParamsDict = {'path': path}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)

        target = _targetPath(path)
        isBranch = fto.branchPredicate(target)
        b_io.ann.note(f"{target}: {'branch' if isBranch else 'not-branch'}")

        if isBranch:
            return cmndOutcome.set(opError=b.op.OpError.Success, opResults=True)
        return cmndOutcome.set(opError=b.op.OpError.Failure, opResults=False)


class fto_leafPredicate(cs.Cmnd):
    """Exit 0 (success) if target is a leaf; failure otherwise."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        callParamsDict = {'path': path}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)

        target = _targetPath(path)
        isLeaf = fto.leafPredicate(target)
        b_io.ann.note(f"{target}: {'leaf' if isLeaf else 'not-leaf'}")

        if isLeaf:
            return cmndOutcome.set(opError=b.op.OpError.Success, opResults=True)
        return cmndOutcome.set(opError=b.op.OpError.Failure, opResults=False)


class fto_effectiveBranches(cs.Cmnd):
    """List the effective child branches beneath the target."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        callParamsDict = {'path': path}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)

        target = _targetPath(path)
        branches = fto.effectiveBranches(target)
        for br in branches:
            print(br)
        return cmndOutcome.set(opError=b.op.OpError.Success, opResults=[str(p) for p in branches])


class fto_effectiveLeaves(cs.Cmnd):
    """List the effective child leaves beneath the target."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        callParamsDict = {'path': path}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)

        target = _targetPath(path)
        leaves = fto.effectiveLeaves(target)
        for lf in leaves:
            print(lf)
        return cmndOutcome.set(opError=b.op.OpError.Success, opResults=[str(p) for p in leaves])


class fto_treeList(cs.Cmnd):
    """Recursive dry-run: print every node beneath the target, prefixed by its type."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        callParamsDict = {'path': path}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)

        target = _targetPath(path)
        visited: list[tuple[str, pathlib.Path]] = []

        def _describe(p: pathlib.Path) -> None:
            obj = fto.FILE_TreeObject(p)
            nt = obj.nodeType()
            label = nt.name if nt else '(no _tree_)'
            visited.append((label, p))
            print(f"  {label:12s}  {p}")

        _describe(target)
        for br in fto.effectiveBranches(target):
            _describe(br)
            # Recursion via treeRecurse would double-print; walk children directly here.
            for sub in fto.effectiveBranches(br):
                _describe(sub)
            for lf in fto.effectiveLeaves(br):
                _describe(lf)
        for lf in fto.effectiveLeaves(target):
            _describe(lf)

        return cmndOutcome.set(opError=b.op.OpError.Success, opResults=visited)


###############################################################################
# ============================ Creation =======================================
###############################################################################

def _createCmnd(
    self,
    rtInv: cs.RtInvoker,
    cmndOutcome: b.op.Outcome,
    path: typing.Optional[str],
    treeProc: typing.Optional[str],
    objectType: typing.Optional[str],
    argsList: typing.Optional[list[str]],
    method: str,
) -> b.op.Outcome:
    """Shared body for the *Create Cmnds. Dispatches to the named
    FILE_TreeObject method with the supplied treeProc/objectType.
    """
    callParamsDict = {'path': path, 'treeProc': treeProc, 'objectType': objectType}
    if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
        return b_io.eh.badOutcome(cmndOutcome)

    target = _targetPath(path)
    obj = fto.FILE_TreeObject(target)

    # ignoreCreate takes no kwargs; the others take treeProc / objectType.
    if method == 'ignoreCreate':
        getattr(obj, method)()
    else:
        getattr(obj, method)(treeProc=treeProc, objectType=objectType)

    b_io.ann.note(f"{method}: {target}")
    if treeProc:
        b_io.ann.note(f"  _treeProc_:   {treeProc}")
    if objectType:
        b_io.ann.note(f"  _objectType_: {objectType}")

    return cmndOutcome.set(opError=b.op.OpError.Success, opResults=str(target))


class fto_branchCreate(cs.Cmnd):
    """Write =_tree_= with =branch= at target."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path', 'treeProc', 'objectType']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        treeProc: typing.Optional[str] = None,
        objectType: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        return _createCmnd(self, rtInv, cmndOutcome, path, treeProc, objectType,
                           argsList, 'branchCreate')


class fto_leafCreate(cs.Cmnd):
    """Write =_tree_= with =leaf= at target."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path', 'treeProc', 'objectType']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        treeProc: typing.Optional[str] = None,
        objectType: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        return _createCmnd(self, rtInv, cmndOutcome, path, treeProc, objectType,
                           argsList, 'leafCreate')


class fto_auxBranchCreate(cs.Cmnd):
    """Write =_tree_= with =auxBranch= at target (traverse but do not apply)."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path', 'treeProc', 'objectType']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        treeProc: typing.Optional[str] = None,
        objectType: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        return _createCmnd(self, rtInv, cmndOutcome, path, treeProc, objectType,
                           argsList, 'auxBranchCreate')


class fto_auxLeafCreate(cs.Cmnd):
    """Write =_tree_= with =auxLeaf= at target (skip application, no error)."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path', 'treeProc', 'objectType']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        treeProc: typing.Optional[str] = None,
        objectType: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        return _createCmnd(self, rtInv, cmndOutcome, path, treeProc, objectType,
                           argsList, 'auxLeafCreate')


class fto_ignoreCreate(cs.Cmnd):
    """Write =_tree_= with =ignore= at target (skip this and everything below)."""
    cmndParamsMandatory = []
    cmndParamsOptional = ['path']
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        path: typing.Optional[str] = None,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        return _createCmnd(self, rtInv, cmndOutcome, path, None, None,
                           argsList, 'ignoreCreate')


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

### local variables:
### no-byte-compile: t
### end:
####+END:
