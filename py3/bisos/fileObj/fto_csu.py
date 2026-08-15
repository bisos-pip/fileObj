# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Unit= (Cmnd-Lib) exposing the =fto_*= surface for
  branch-side introspection and node creation. Consumed by =ftoBranch-seed.cs=.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-lib"
""" #+begin_org
* [[elisp:(org-cycle)][| /Control Parameters Of This File/ |]] :: dblk ctrls classifications=cs-lib
#+BEGIN_SRC emacs-lisp
(setq-local b:dblockControls t) ; (setq-local b:dblockControls nil)
(put 'b:dblockControls 'py3:cs:Classification "cs-lib") ; one of cs-mu, cs-u, cs-lib, bpf-lib, pyLibPure
#+END_SRC
#+RESULTS:
: cs-lib
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
** This File: /bisos/git/bxRepos/bisos-pip/fileObj/py3/bisos/fileObj/fto_csu.py
** File True Name: /bisos/git/auth/bxRepos/bisos-pip/fileObj/py3/bisos/fileObj/fto_csu.py
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
csInfo['panel'] = 'fto_csu-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: The =fto_*= Cmnd surface.
Three groups:
- *Introspection*: =fto_nodeInfo=, =fto_branchPredicate=, =fto_leafPredicate=,
  =fto_effectiveBranches=, =fto_effectiveLeaves=, =fto_treeList=.
- *Creation*: =fto_branchCreate=, =fto_leafCreate=, =fto_auxBranchCreate=,
  =fto_auxLeafCreate=, =fto_ignoreCreate=.
- *Forwarding* (Stage 2): =fto_forwardToLeaves= (Mode 1 --- leaf-side
  verb: invokes =<leafDir>/<_treeProc_> -i <cmndName>= at each effective
  leaf) and =fto_walkRunExternal= (Mode 2 --- external cmnd: runs an
  arbitrary cmnd at every visited node, resolved from the node dir or
  PATH). See AI-WorkPlan Stage 2 for the design.

All commands operate on a target directory identified by =--path= (defaults
to cwd, or to the planted branch when running under =ftoBranchProc.spcs=).
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

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CsFrmWrk   *Imports* =Based on Classification=cs-lib=
#+end_org """
from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.common import csParam

import collections
####+END:

import typing
import pathlib
import shutil
import subprocess

from bisos.fileObj import fto
from bisos.fileObj import ftoBranch_seedInfo


####+BEGIN: b:py3:cs:orgItem/section :title "Common Parameters Specification" :comment "based on cs.param.CmndParamDict -- As expected from CSU-s"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  /Section/    [[elisp:(outline-show-subtree+toggle)][||]] *Common Parameters Specification* based on cs.param.CmndParamDict
#+end_org """
####+END:

def commonParamsSpecify(
        csParams: cs.param.CmndParamDict,
) -> None:
    """Register the CS parameters used by fto_* Cmnds."""
    csParams.parDictAdd(
        parName='path',
        parDescription="Target directory (defaults to cwd, or the planted branch under ftoBranchProc.spcs).",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        argparseShortOpt=None,
        argparseLongOpt='--path',
    )
    csParams.parDictAdd(
        parName='treeProc',
        parDescription="Name of the executable to record in _treeProc_ (for fto_*Create Cmnds).",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        argparseShortOpt=None,
        argparseLongOpt='--treeProc',
    )
    csParams.parDictAdd(
        parName='objectType',
        parDescription="Object-type tag to record in _objectType_ (for fto_*Create Cmnds).",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        argparseShortOpt=None,
        argparseLongOpt='--objectType',
    )
    csParams.parDictAdd(
        parName='cmndName',
        parDescription="Cmnd verb to forward to each leaf's _treeProc_ (for fto_forwardToLeaves).",
        parDataType=None,
        parDefault=None,
        parChoices=list(),
        argparseShortOpt=None,
        argparseLongOpt='--cmndName',
    )
    csParams.parDictAdd(
        parName='recurseMode',
        parDescription="Sub-branch recursion mode: 'subprocess' (default) invokes each sub-branch's own ftoBranchProc.spcs so it can re-establish its own domain context; 'inProcess' recurses in a single Python process (faster, but only correct for homogeneous trees).",
        parDataType=None,
        parDefault=None,
        parChoices=['subprocess', 'inProcess'],
        argparseShortOpt=None,
        argparseLongOpt='--recurseMode',
    )


###############################################################################
# Helpers
###############################################################################

def _resolveTargetPath(path: typing.Optional[str]) -> pathlib.Path:
    """Resolve the effective target directory for a Cmnd invocation.

    Precedence:
    1. Explicit =--path= parameter.
    2. Planted branch (=ftoBranch_seedInfo.paramsFromPlantPath()=) if we
       are inside a plant context.
    3. Current working directory.
    """
    if path is not None:
        return pathlib.Path(path).resolve()

    try:
        params = ftoBranch_seedInfo.paramsFromPlantPath()
        return params.branchPath
    except ValueError:
        return pathlib.Path.cwd()


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Direct Command Services" :anchor ""  :extraInfo "Examples and CSs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  [[elisp:(outline-show-subtree+toggle)][| _Direct Command Services_: |]]  Examples and CSs  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "examples_csu" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "" :argsMin 0 :argsMax 0 :pyInv "pyKwArgs"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<examples_csu>>  =verify= ro=cli pyInv=pyKwArgs
#+end_org """
class examples_csu(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             pyKwArgs: typing.Any=None,   # pyInv Argument
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Examples menu for the fto_* Cmnd surface.
Two groups: *Introspection* (fto_nodeInfo, fto_branchPredicate, etc.)
and *Creation* (fto_branchCreate, fto_leafCreate, etc.).
        #+end_org """)

        od = collections.OrderedDict
        cmnd = cs.examples.cmndEnter

        cs.examples.menuChapter('=fto_*= --- Introspection Cmnds')

        cmnd('fto_nodeInfo',          comment="# print _tree_ / _treeProc_ / _objectType_ at target")
        cmnd('fto_branchPredicate',   comment="# exit 0 if target is a branch")
        cmnd('fto_leafPredicate',     comment="# exit 0 if target is a leaf")
        cmnd('fto_effectiveBranches', comment="# list child branches at target")
        cmnd('fto_effectiveLeaves',   comment="# list child leaves at target")
        cmnd('fto_treeList',          comment="# recursive list of every node beneath target")

        cs.examples.menuChapter('=fto_*Create= --- Node-Creation Cmnds')

        cmnd('fto_branchCreate',      comment="# mark cwd as a branch")
        cmnd('fto_branchCreate',      pars=od([('treeProc', 'ftoBranchProc.spcs')]),
                                      comment="# ... with a _treeProc_")
        cmnd('fto_leafCreate',        comment="# mark cwd as a leaf")
        cmnd('fto_leafCreate',        pars=od([('treeProc', 'someHandler.sh')]),
                                      comment="# ... with a _treeProc_")
        cmnd('fto_auxBranchCreate',   comment="# traverse but skip processing")
        cmnd('fto_auxLeafCreate',     comment="# skip application, no error")
        cmnd('fto_ignoreCreate',      comment="# skip this and everything below")

        # -------------------------------------------------------------
        # Forwarding + Walks --- source of truth is the branch's .spcs
        # (via ftoBranch_seedInfo.setup(leafExamples=...)) which typically
        # pulls the list from its leaf-side seed. See AI-WorkPlan Stage 2
        # "Leaf-seed-owned walk examples" for the design.
        # -------------------------------------------------------------
        cs.examples.menuChapter('=fto_forward*= --- Forwarding Cmnds (Mode 1: leaf-side verbs)')
        cmnd('fto_forwardToLeaves',
             pars=od([('cmndName', '<leafVerb>')]),
             comment="# invoke each leaf's _treeProc_ -i <leafVerb>  (see leafExamples below)")

        cs.examples.menuChapter('=fto_walkRun*= --- External-Cmnd Walks (Mode 2)')
        cmnd('fto_walkRunExternal',   args="<externalCmnd> [args...]",
                                      comment="# run <externalCmnd> at every visited node  (see leafExamples below)")
        cmnd('fto_walkRunExternal',   args="ls -la _tree_",
                                      comment="# generic diagnostic: read every node's _tree_ marker")

        # -------------------------------------------------------------
        # Leaf-provided examples (typed) --- rendered from ftoBranchSeedInfo.leafExamples.
        # A branch .spcs populates this list by importing its leaf-side seed's
        # walkExamples() function and passing the result to setup(leafExamples=...).
        # -------------------------------------------------------------
        leafExamples = ftoBranch_seedInfo.ftoBranchSeedInfo.leafExamples
        if leafExamples:
            mode1 = [s for s in leafExamples if s.mode == 'forwardToLeaves']
            mode2 = [s for s in leafExamples if s.mode == 'walkRunExternal']

            if mode1:
                cs.examples.menuChapter('=Leaf-Provided Walk Examples (Mode 1)=')
                for spec in mode1:
                    pars = od([('cmndName', spec.cmndName)])
                    pars.update(spec.pars)
                    cmnd('fto_forwardToLeaves', pars=pars, comment=spec.comment or "")

            if mode2:
                cs.examples.menuChapter('=Leaf-Provided Walk Examples (Mode 2)=')
                for spec in mode2:
                    argStr = f"{spec.cmndName} {spec.args}".rstrip()
                    cmnd('fto_walkRunExternal', args=argStr, comment=spec.comment or "")

        return(cmndOutcome)


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Introspection Cmnds" :anchor ""  :extraInfo "fto_nodeInfo etc."
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  [[elisp:(outline-show-subtree+toggle)][| _Introspection Cmnds_: |]]  fto_nodeInfo etc.  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_nodeInfo" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_nodeInfo>>  =verify= parsOpt=path ro=cli
#+end_org """
class fto_nodeInfo(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Print _tree_, _treeProc_, _objectType_ at target directory.
        #+end_org """)

        target = _resolveTargetPath(path)
        node = fto.FILE_TreeObject(target)

        nt = node.nodeType()
        tp = node.treeProc()
        ot = node.objectType()

        report = (
            f"Node info for: {target}\n"
            f"  _tree_        : {nt.name if nt else '(none)'}\n"
            f"  _treeProc_    : {tp if tp else '(none)'}\n"
            f"  _objectType_  : {ot if ot else '(none)'}"
        )
        b_io.ann.write(report)

        return cmndOutcome.set(opResults=report)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_branchPredicate" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_branchPredicate>>  =verify= parsOpt=path ro=cli
#+end_org """
class fto_branchPredicate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Return True if target is a branch.
        #+end_org """)

        target = _resolveTargetPath(path)
        isBranch = fto.branchPredicate(target)

        b_io.ann.write(f"branchPredicate({target}) = {isBranch}")

        return cmndOutcome.set(opResults=isBranch)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_leafPredicate" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_leafPredicate>>  =verify= parsOpt=path ro=cli
#+end_org """
class fto_leafPredicate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Return True if target is a leaf, else False.
        #+end_org """)

        target = _resolveTargetPath(path)
        isLeaf = fto.leafPredicate(target)

        b_io.ann.write(f"leafPredicate({target}) = {isLeaf}")

        return cmndOutcome.set(opResults=isLeaf)


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_effectiveBranches" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_effectiveBranches>>  =verify= parsOpt=path ro=cli
#+end_org """
class fto_effectiveBranches(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  List the effective child branches at target.
Honors module-level control parameters from the planted .spcs
(=branchesList=, =branchesExcludes=, =branchesOrdered=) if set.
        #+end_org """)

        target = _resolveTargetPath(path)
        si = ftoBranch_seedInfo.ftoBranchSeedInfo

        branches = fto.effectiveBranches(
            target,
            branchesList=si.branchesList,
            branchesExcludes=si.branchesExcludes,
            branchesOrdered=si.branchesOrdered,
        )
        for p in branches:
            b_io.ann.write(str(p))

        return cmndOutcome.set(opResults=[str(p) for p in branches])


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_effectiveLeaves" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_effectiveLeaves>>  =verify= parsOpt=path ro=cli
#+end_org """
class fto_effectiveLeaves(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  List the effective child leaves at target.
Honors module-level control parameters (=leavesList=, =leavesExcludes=,
=leavesOrdered=) if set.
        #+end_org """)

        target = _resolveTargetPath(path)
        si = ftoBranch_seedInfo.ftoBranchSeedInfo

        leaves = fto.effectiveLeaves(
            target,
            leavesList=si.leavesList,
            leavesExcludes=si.leavesExcludes,
            leavesOrdered=si.leavesOrdered,
        )
        for p in leaves:
            b_io.ann.write(str(p))

        return cmndOutcome.set(opResults=[str(p) for p in leaves])


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_treeList" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_treeList>>  =verify= parsOpt=path ro=cli
#+end_org """
class fto_treeList(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Recursive dry-run list of every node beneath target.
Uses =treeRecurse= with a collect-only callable (no side effects).
        #+end_org """)

        target = _resolveTargetPath(path)
        collected: list[str] = []
        leafProcessors = ftoBranch_seedInfo.ftoBranchSeedInfo.leafProcessors

        def _collect(node: fto.FILE_TreeObject) -> bool:
            nt = node.nodeType(leafProcessors=leafProcessors)
            tag = nt.name if nt else '(none)'
            collected.append(f"{tag}: {node.fileTreeBasePath()}")
            return True

        fto.treeRecurse(target, _collect)

        for line in collected:
            b_io.ann.write(line)

        return cmndOutcome.set(opResults=collected)


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Creation Cmnds" :anchor ""  :extraInfo "fto_branchCreate etc."
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  [[elisp:(outline-show-subtree+toggle)][| _Creation Cmnds_: |]]  fto_branchCreate etc.  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_branchCreate" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path treeProc objectType" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_branchCreate>>  =verify= parsOpt="path treeProc objectType" ro=cli
#+end_org """
class fto_branchCreate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', 'treeProc', 'objectType', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
             treeProc: typing.Optional[str]=None,
             objectType: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, 'treeProc': treeProc, 'objectType': objectType, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
        treeProc = csParam.mappedValue('treeProc', treeProc)
        objectType = csParam.mappedValue('objectType', objectType)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Mark target as a =branch=.
Writes =_tree_= with contents =branch=. Optionally writes =_treeProc_=
and =_objectType_= if provided.
        #+end_org """)

        target = _resolveTargetPath(path)
        fto.FILE_TreeObject(target).branchCreate(treeProc=treeProc, objectType=objectType)

        b_io.ann.write(f"branchCreate: {target}")
        return cmndOutcome.set(opResults=str(target))


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_leafCreate" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path treeProc objectType" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_leafCreate>>  =verify= parsOpt="path treeProc objectType" ro=cli
#+end_org """
class fto_leafCreate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', 'treeProc', 'objectType', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
             treeProc: typing.Optional[str]=None,
             objectType: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, 'treeProc': treeProc, 'objectType': objectType, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
        treeProc = csParam.mappedValue('treeProc', treeProc)
        objectType = csParam.mappedValue('objectType', objectType)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Mark target as a =leaf=.
        #+end_org """)

        target = _resolveTargetPath(path)
        fto.FILE_TreeObject(target).leafCreate(treeProc=treeProc, objectType=objectType)

        b_io.ann.write(f"leafCreate: {target}")
        return cmndOutcome.set(opResults=str(target))


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_auxBranchCreate" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path treeProc objectType" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_auxBranchCreate>>  =verify= parsOpt="path treeProc objectType" ro=cli
#+end_org """
class fto_auxBranchCreate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', 'treeProc', 'objectType', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
             treeProc: typing.Optional[str]=None,
             objectType: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, 'treeProc': treeProc, 'objectType': objectType, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
        treeProc = csParam.mappedValue('treeProc', treeProc)
        objectType = csParam.mappedValue('objectType', objectType)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Mark target as an =auxBranch= (traverse but do not apply).
        #+end_org """)

        target = _resolveTargetPath(path)
        fto.FILE_TreeObject(target).auxBranchCreate(treeProc=treeProc, objectType=objectType)

        b_io.ann.write(f"auxBranchCreate: {target}")
        return cmndOutcome.set(opResults=str(target))


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_auxLeafCreate" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path treeProc objectType" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_auxLeafCreate>>  =verify= parsOpt="path treeProc objectType" ro=cli
#+end_org """
class fto_auxLeafCreate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', 'treeProc', 'objectType', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
             treeProc: typing.Optional[str]=None,
             objectType: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, 'treeProc': treeProc, 'objectType': objectType, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
        treeProc = csParam.mappedValue('treeProc', treeProc)
        objectType = csParam.mappedValue('objectType', objectType)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Mark target as an =auxLeaf= (skip application, no error).
        #+end_org """)

        target = _resolveTargetPath(path)
        fto.FILE_TreeObject(target).auxLeafCreate(treeProc=treeProc, objectType=objectType)

        b_io.ann.write(f"auxLeafCreate: {target}")
        return cmndOutcome.set(opResults=str(target))


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_ignoreCreate" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_ignoreCreate>>  =verify= parsOpt=path ro=cli
#+end_org """
class fto_ignoreCreate(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Mark target as =ignore= (skip this and everything below).
        #+end_org """)

        target = _resolveTargetPath(path)
        fto.FILE_TreeObject(target).ignoreCreate()

        b_io.ann.write(f"ignoreCreate: {target}")
        return cmndOutcome.set(opResults=str(target))


####+BEGIN: blee:bxPanel:foldingSection :outLevel 0 :sep nil :title "Forwarding Cmnds" :anchor ""  :extraInfo "fto_forwardToLeaves etc."
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  [[elisp:(outline-show-subtree+toggle)][| _Forwarding Cmnds_: |]]  fto_forwardToLeaves etc.  [[elisp:(org-shifttab)][<)]] E|
#+end_org """
####+END:

####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_forwardToLeaves" :extent "verify" :ro "cli" :comment "" :parsMand "cmndName" :parsOpt "path recurseMode" :argsMin 0 :argsMax 0 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_forwardToLeaves>>  =verify= parsMand=cmndName parsOpt="path recurseMode" ro=cli
#+end_org """
class fto_forwardToLeaves(cs.Cmnd):
    cmndParamsMandatory = [ 'cmndName', ]
    cmndParamsOptional = [ 'path', 'recurseMode', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             cmndName: typing.Optional[str]=None,
             path: typing.Optional[str]=None,
             recurseMode: typing.Optional[str]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'cmndName': cmndName, 'path': path, 'recurseMode': recurseMode, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, None).isProblematic():
            return failed(cmndOutcome)
        cmndName = csParam.mappedValue('cmndName', cmndName)
        path = csParam.mappedValue('path', path)
        recurseMode = csParam.mappedValue('recurseMode', recurseMode)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Forward =-i <cmndName>= to every effective leaf.

Mode 1 walk (per Stage 2 design): the =cmndName= is a Cmnd verb that
the leaf's own =_treeProc_= dispatcher must understand. At each leaf,
the walker invokes =<leafDir>/<_treeProc_> -i <cmndName>= via
subprocess.

The branch itself is NOT applied --- forwarding targets leaves only.
Honors =ftoBranchSeedInfo.leavesList=, =leavesExcludes=, =leavesOrdered=
overrides.

*Sub-branch recursion:* by default (=recurseMode=subprocess=) each
sub-branch that has its own =ftoBranchProc.spcs= is invoked as a
*subprocess* --- =./ftoBranchProc.spcs -i fto_forwardToLeaves
--cmndName=<X>= at the sub-branch dir. That subprocess re-establishes
its own domain context (its own =leafProcessors=, its own
=walkExamples=) and streams its own results to its own stdout. The
parent WalkResult only records "handed off here" for such sub-branches
--- results are NOT merged. This is what makes heterogeneous walks
possible (docker sub-branch and pypi sub-branch under one root).

Use =recurseMode=inProcess= for homogeneous trees where subprocess
spawn overhead is undesirable and singleton state is safe to share
across sub-branches.

Exit-code caveat (Stage 2 TODO [#C]): =bisos.b.cs.main.g_csMain= exits 0
even when the invoked Cmnd raises. =WalkResult.failed= therefore may
under-report genuine leaf failures. Inspect stderr for real error
signals until the =bisos.b= exit-code propagation is fixed upstream.
        #+end_org """)

        target = _resolveTargetPath(path)
        si = ftoBranch_seedInfo.ftoBranchSeedInfo

        # Default is subprocess dispatch; only inProcess if explicitly requested.
        if recurseMode == 'inProcess':
            subBranchArgv = None
        else:
            subBranchArgv = ['-i', 'fto_forwardToLeaves', f'--cmndName={cmndName}']

        result = fto.treeRecurse(
            target,
            ['-i', cmndName],
            applyAtBranch=False,
            applyAtLeaf=True,
            leavesList=si.leavesList,
            leavesExcludes=si.leavesExcludes,
            leavesOrdered=si.leavesOrdered,
            branchesList=si.branchesList,
            branchesExcludes=si.branchesExcludes,
            branchesOrdered=si.branchesOrdered,
            subBranchArgv=subBranchArgv,
        )

        b_io.ann.write(
            f"fto_forwardToLeaves --cmndName={cmndName!r}:  "
            f"visited={len(result.visited)}  "
            f"failed={len(result.failed)}  "
            f"skipped={len(result.skipped)}"
        )
        for p in result.visited:
            b_io.ann.write(f"  visited: {p}")
        for p in result.failed:
            b_io.ann.write(f"  FAILED:  {p}")
        for p in result.skipped:
            b_io.ann.write(f"  skipped: {p}")

        return cmndOutcome.set(opResults={
            'visited': [str(p) for p in result.visited],
            'failed':  [str(p) for p in result.failed],
            'skipped': [str(p) for p in result.skipped],
        })


####+BEGIN: b:py3:cs:cmnd/classHead :cmndName "fto_walkRunExternal" :extent "verify" :ro "cli" :comment "" :parsMand "" :parsOpt "path recurseMode" :argsMin 1 :argsMax 9999 :pyInv ""
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_  CmndSvc-   [[elisp:(outline-show-subtree+toggle)][||]] <<fto_walkRunExternal>>  =verify= parsOpt="path recurseMode" ro=cli
#+end_org """
class fto_walkRunExternal(cs.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'path', 'recurseMode', ]
    cmndArgsLen = {'Min': 1, 'Max': 9999,}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
             rtInv: cs.RtInvoker,
             cmndOutcome: b.op.Outcome,
             path: typing.Optional[str]=None,
             recurseMode: typing.Optional[str]=None,
             argsList: typing.Optional[list[str]]=None,
    ) -> b.op.Outcome:

        failed = b_io.eh.badOutcome
        callParamsDict = {'path': path, 'recurseMode': recurseMode, }
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return failed(cmndOutcome)
        path = csParam.mappedValue('path', path)
        recurseMode = csParam.mappedValue('recurseMode', recurseMode)
####+END:
        self.cmndDocStr(f""" #+begin_org
** [[elisp:(org-cycle)][| *CmndDesc:* | ]]  Run an external command at every visited node.

Mode 2 walk (per Stage 2 design): =argsList[0]= is an external
executable; =argsList[1:]= are its args. At each visited node
(branch, auxBranch, leaf --- but NOT auxLeaf, NOT ignore), the walker
attempts to run the external command from that node's directory.

Resolution ("perhapsRun"): the executable is looked up first in the
node directory itself, then via =shutil.which()=. If neither resolves,
the node is silently skipped with a note --- the walk continues.

Matches bash =ftoWalkRunCmnd= semantics. The leaf's =_treeProc_= is
NOT consulted for what to run --- only as a marker (=leaf= vs
=auxLeaf= vs no marker) governing whether the walker visits at all.

*Sub-branch recursion:* by default (=recurseMode=subprocess=) each
sub-branch that has its own =ftoBranchProc.spcs= is invoked as a
subprocess with the same external cmnd + args. That sub-branch
re-establishes its own domain context and streams its own results.
Use =recurseMode=inProcess= for homogeneous trees.

Examples:
  ftoBranchProc.spcs -i fto_walkRunExternal gitStatusReport
  ftoBranchProc.spcs -i fto_walkRunExternal ls -la _tree_
        #+end_org """)

        if not argsList:
            b_io.eh.problem_usageError("fto_walkRunExternal requires at least one argument (the external cmnd)")
            return failed(cmndOutcome)

        argv = list(argsList)
        target = _resolveTargetPath(path)
        si = ftoBranch_seedInfo.ftoBranchSeedInfo

        # Default is subprocess dispatch; inProcess only if explicitly requested.
        if recurseMode == 'inProcess':
            subBranchArgv = None
        else:
            subBranchArgv = ['-i', 'fto_walkRunExternal', *argv]

        # perhapsRun-shaped callable: at each node, resolve argv[0] and run.
        externalRan: dict = {'ok': 0, 'fail': 0, 'skip': 0}

        def externalRunner(node: fto.FILE_TreeObject) -> bool:
            cmnd = argv[0]
            nodeDir = node.fileTreeBasePath()
            # Node dir first, then PATH.
            candidate = nodeDir / cmnd
            if candidate.is_file():
                execPath = str(candidate)
            else:
                whichPath = shutil.which(cmnd)
                if whichPath is None:
                    b_io.ann.write(f"  skip: {cmnd!r} not resolvable at {nodeDir}")
                    externalRan['skip'] += 1
                    return True   # skipped-but-not-a-failure; walker continues
                execPath = whichPath
            b_io.ann.write(f"  RUN [{nodeDir}]:  {execPath} {' '.join(argv[1:])}")
            try:
                proc = subprocess.run(
                    [execPath, *argv[1:]],
                    cwd=str(nodeDir),
                    check=False,
                )
            except Exception as exc:
                b_io.ann.write(f"  exec-fail at {nodeDir}: {exc!r}")
                externalRan['fail'] += 1
                return False
            if proc.returncode == 0:
                externalRan['ok'] += 1
                return True
            b_io.ann.write(f"  exit={proc.returncode} at {nodeDir}")
            externalRan['fail'] += 1
            return False

        result = fto.treeRecurse(
            target,
            externalRunner,
            applyAtBranch=True,
            applyAtLeaf=True,
            leavesList=si.leavesList,
            leavesExcludes=si.leavesExcludes,
            leavesOrdered=si.leavesOrdered,
            branchesList=si.branchesList,
            branchesExcludes=si.branchesExcludes,
            branchesOrdered=si.branchesOrdered,
            subBranchArgv=subBranchArgv,
        )

        b_io.ann.write(
            f"fto_walkRunExternal {argv!r}:  "
            f"visited={len(result.visited)}  "
            f"ran-ok={externalRan['ok']}  "
            f"ran-fail={externalRan['fail']}  "
            f"cmnd-skip={externalRan['skip']}  "
            f"walker-skip={len(result.skipped)}"
        )

        return cmndOutcome.set(opResults={
            'argv': argv,
            'visited': [str(p) for p in result.visited],
            'ranOk':   externalRan['ok'],
            'ranFail': externalRan['fail'],
            'cmndSkip': externalRan['skip'],
            'walkerSkip': [str(p) for p in result.skipped],
        })


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

#+STARTUP: showall

### local variables:
### no-byte-compile: t
### end:
####+END:
