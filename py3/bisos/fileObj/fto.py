# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: =PyLib= for File Tree Objects (FTO) --- filesystem-directory-backed
  tree data structure + walker. Python port of the bash reference at
  =/bisos/core/bsip/bin/lcnObjectTree.libSh=, with corrected branch/leaf
  vocabulary.
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
** This File: /bxRepos/bisos-pip/fileObj/py3/bisos/fileObj/fto.py
** File True Name: /bisos/git/auth/bxRepos/bisos-pip/fileObj/py3/bisos/fileObj/fto.py
** Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
#+end_org """
####+END:

####+BEGIN: b:py3:file/particulars-csInfo :status "inDev"
""" #+begin_org
* *[[elisp:(org-cycle)][| Particulars-csInfo |]]*
#+end_org """
import typing
csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['fto'], }
csInfo['version'] = '202608120001'
csInfo['status']  = 'inDev'
csInfo['panel'] = 'fto-Panel.org'
csInfo['groupingType'] = 'IcmGroupingType-pkged'
csInfo['cmndParts'] = 'IcmCmndParts[common] IcmCmndParts[param]'
####+END:

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]]
File Tree Object (FTO) library. Provides:

- =FileTreeItem= enum: node type marker values (Branch, Leaf, AuxBranch,
  AuxLeaf, Ignore).
- =FILE_TreeObject= class: represents one node (directory) in the tree,
  with create / read / predicate methods.
- Walker functions: =treeRecurse=, =effectiveBranches=, =effectiveLeaves=,
  =branchPredicate=, =leafPredicate=.

Marker file conventions (matches the bash reference):
- =_tree_= --- one line naming the node type (branch / leaf / auxBranch /
  auxLeaf / ignore). Backward-compat: reads bash-written =node= as Branch
  and =auxNode= as AuxBranch.
- =_treeProc_= --- one line naming the executable that processes this node.
- =_objectType_= --- optional metadata (e.g. =fto.leaf=, =bxt.custom=).

Vocabulary correction: the bash implementation uses "node" for what a
proper tree data structure calls a "branch." A tree is made of nodes;
each node is either a branch (has children) or a leaf (endpoint). This
Python port writes =branch= going forward; reads bash-written =node= for
compatibility.

** Status: inDev (Stage 1 scaffolding)
** Relevant Panels:
- =/bisos/git/auth/bxRepos/bisos-pip/fileObj/py3/panels/bisos.fileObj/=

** Bash reference:
- =/bisos/core/bsip/bin/lcnObjectTree.libSh=
- =/bisos/core/bsip/bin/seedFtoCommon.sh=
- =/bisos/core/bsip/bin/ftoProc.sh=
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Controls |]] :: [[elisp:(delete-other-windows)][(1)]] | [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
#+end_org """
####+END:

####+BEGIN: b:py3:file/workbench :outLevel 1
""" #+begin_org
* [[elisp:(org-cycle)][| Workbench |]] :: [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "/bisos/venv/py3/bisos3/bin/python -m pydoc ./%s" (bx:buf-fname))))][pydoc]]
#+end_org """
####+END:

####+BEGIN: b:py3:cs:framework/imports :basedOn "classification"
""" #+begin_org
*  _[[elisp:(blee:menu-sel:outline:popupMenu)][±]]_ _[[elisp:(blee:menu-sel:navigation:popupMenu)][Ξ]]_    CsFrmWrk *Imports* =Based on Classification=cs-lib=
#+end_org """
from bisos import b
from bisos.b import b_io

import enum
import pathlib
import subprocess
import shutil
from dataclasses import dataclass, field
####+END:


###############################################################################
# FileTreeItem --- enum of node type markers.
# Matches the bash reference's treeItemEnum in lcnObjectTree.libSh, but with
# corrected vocabulary (branch, not node). Backward-compat read handles bash's
# legacy strings.
###############################################################################

class FileTreeItem(enum.Enum):
    """Enum of tree-item classifications (=_tree_= file contents).

    Corrected vocabulary --- the bash implementation uses =node= for what a
    proper tree data structure calls a =branch=. Python writes =branch=
    going forward. Reads accept both.
    """
    Branch    = 'branch'
    Leaf      = 'leaf'
    AuxBranch = 'auxBranch'
    AuxLeaf   = 'auxLeaf'
    Ignore    = 'ignore'

    @classmethod
    def fromString(cls, s: str) -> 'FileTreeItem':
        """Parse a =_tree_= file's contents into a FileTreeItem.

        Recognizes the current Python vocabulary AND the legacy bash
        vocabulary (=node=, =auxNode=). Case-sensitive on the current
        vocabulary; the legacy strings are matched exactly as they were
        written by the bash implementation.
        """
        s = s.strip()
        # Legacy bash compatibility
        if s == 'node':
            return cls.Branch
        if s == 'auxNode':
            return cls.AuxBranch
        if s == 'ignoreNode':
            return cls.AuxBranch    # bash deprecated alias
        if s == 'ignoreLeaf':
            return cls.AuxLeaf      # bash deprecated alias
        # Current vocabulary
        for member in cls:
            if member.value == s:
                return member
        raise ValueError(f"Unknown _tree_ value: {s!r}")


###############################################################################
# Marker file names --- constants matching the bash reference.
###############################################################################

TREE_MARKER_FILE       = '_tree_'
TREE_PROC_FILE         = '_treeProc_'
TREE_OBJECT_TYPE_FILE  = '_objectType_'


###############################################################################
# FILE_TreeObject --- one node in the tree.
# Parallels the bash FILE_TreeObject class from lcnObjectTree.libSh (which
# is itself paralleled by bisos.b.fto.FILE_TreeObject).
###############################################################################

class FILE_TreeObject:
    """One node in a filesystem tree.

    A node's identity IS its directory path. Its role in the tree
    (branch / leaf / etc.) is recorded in the =_tree_= marker file
    inside that directory.

    Bash reference: FILE_TreeObject in lcnObjectTree.libSh.
    """

    def __init__(self, fileSysPath: typing.Union[str, pathlib.Path]):
        self._basePath = pathlib.Path(fileSysPath)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def fileTreeBasePath(self) -> pathlib.Path:
        return self._basePath

    # ------------------------------------------------------------------
    # Create --- write marker files
    # ------------------------------------------------------------------

    def _createWithMarker(
        self,
        item: FileTreeItem,
        treeProc: typing.Optional[str] = None,
        objectType: typing.Optional[str] = None,
    ) -> None:
        """Common backend for the *Create() methods. Ensures the directory
        exists, writes =_tree_= with the item's string value, and optionally
        writes =_treeProc_= and =_objectType_=.
        """
        self._basePath.mkdir(parents=True, exist_ok=True)
        (self._basePath / TREE_MARKER_FILE).write_text(item.value + '\n')
        if treeProc is not None:
            (self._basePath / TREE_PROC_FILE).write_text(treeProc + '\n')
        if objectType is not None:
            (self._basePath / TREE_OBJECT_TYPE_FILE).write_text(objectType + '\n')

    def branchCreate(
        self,
        treeProc: typing.Optional[str] = None,
        objectType: typing.Optional[str] = None,
    ) -> None:
        """Mark this directory as a branch."""
        self._createWithMarker(FileTreeItem.Branch, treeProc, objectType)

    def leafCreate(
        self,
        treeProc: typing.Optional[str] = None,
        objectType: typing.Optional[str] = None,
    ) -> None:
        """Mark this directory as a leaf."""
        self._createWithMarker(FileTreeItem.Leaf, treeProc, objectType)

    def auxBranchCreate(
        self,
        treeProc: typing.Optional[str] = None,
        objectType: typing.Optional[str] = None,
    ) -> None:
        """Mark this directory as an auxBranch (traverse but do not apply)."""
        self._createWithMarker(FileTreeItem.AuxBranch, treeProc, objectType)

    def auxLeafCreate(
        self,
        treeProc: typing.Optional[str] = None,
        objectType: typing.Optional[str] = None,
    ) -> None:
        """Mark this directory as an auxLeaf (skip application, do not error)."""
        self._createWithMarker(FileTreeItem.AuxLeaf, treeProc, objectType)

    def ignoreCreate(self) -> None:
        """Mark this directory (and everything below) as ignored."""
        self._createWithMarker(FileTreeItem.Ignore)

    # ------------------------------------------------------------------
    # Read --- inspect marker files
    # ------------------------------------------------------------------

    def nodeType(
            self,
            leafProcessors: typing.Optional[list[str]] = None,
    ) -> typing.Optional[FileTreeItem]:
        """Return the node's FileTreeItem.

        Classification rules (highest priority first):
        1. =_tree_= marker file present → use its value (=Ignore= wins
           over everything below).
        2. =leafProcessors= given and any of those filenames exists in
           this directory → =Leaf= (definitional: presence of a leaf
           processor MEANS this is a leaf).
        3. Absent any marker → =AuxBranch= by default (Idea 2:
           pass-through) when =leafProcessors= is provided; =None=
           otherwise (unclassified --- caller decides).

        The rule 3 behavior differs based on whether =leafProcessors= is
        passed at all: passing it (even an empty list) opts into the
        auxBranch default; passing =None= preserves the legacy
        =None=-means-unclassified semantic used by callers that don't
        know about the walkable-tree context.
        """
        markerPath = self._basePath / TREE_MARKER_FILE
        if markerPath.is_file():
            explicit = FileTreeItem.fromString(markerPath.read_text())
            # Rule 1: explicit =Ignore=, =AuxLeaf=, =AuxBranch=, =Branch=
            # all take precedence. =_tree_=leaf= is redundant with a leaf
            # processor being present, but honored.
            return explicit

        # Rule 2: leaf-processor detection (definitional).
        if leafProcessors:
            for procName in leafProcessors:
                if (self._basePath / procName).is_file():
                    return FileTreeItem.Leaf

        # Rule 3: default AuxBranch when we know we're in a walkable tree
        # (leafProcessors was passed --- possibly empty but not None);
        # None (unclassified) otherwise.
        if leafProcessors is not None:
            return FileTreeItem.AuxBranch
        return None

    def treeProc(
            self,
            leafProcessors: typing.Optional[list[str]] = None,
    ) -> typing.Optional[str]:
        """Return the =_treeProc_= value.

        Resolution order:
        1. =_treeProc_= file present → its value.
        2. =leafProcessors= given and one exists in this directory → that
           filename (first match wins).
        3. =leafProcessors= given and this is (or defaults to) a walkable
           auxBranch → =ftoBranchProc.spcs= (the Idea 2 default).
        4. Otherwise → =None=.
        """
        procPath = self._basePath / TREE_PROC_FILE
        if procPath.is_file():
            return procPath.read_text().strip()

        if leafProcessors:
            for procName in leafProcessors:
                if (self._basePath / procName).is_file():
                    return procName

        if leafProcessors is not None:
            # Auto-AuxBranch default: the branch processor is the
            # ftoBranchProc.spcs that the walker itself was invoked from.
            return 'ftoBranchProc.spcs'

        return None

    def objectType(self) -> typing.Optional[str]:
        """Return the =_objectType_= value, or None if absent."""
        typePath = self._basePath / TREE_OBJECT_TYPE_FILE
        if not typePath.is_file():
            return None
        return typePath.read_text().strip()

    # ------------------------------------------------------------------
    # Predicates
    # ------------------------------------------------------------------

    def isBranch(self) -> bool:
        return self.nodeType() == FileTreeItem.Branch

    def isLeaf(self) -> bool:
        return self.nodeType() == FileTreeItem.Leaf

    def isAuxBranch(self) -> bool:
        return self.nodeType() == FileTreeItem.AuxBranch

    def isAuxLeaf(self) -> bool:
        return self.nodeType() == FileTreeItem.AuxLeaf

    def isIgnore(self) -> bool:
        return self.nodeType() == FileTreeItem.Ignore


###############################################################################
# Module-level walker functions.
# These are the bash reference's vis_effectiveLeaves / vis_effectiveNodes /
# vis_treeRecurse as free-standing Python functions. Deliberately not methods
# on FILE_TreeObject --- the walker operates *across* many nodes.
###############################################################################

def branchPredicate(path: typing.Union[str, pathlib.Path]) -> bool:
    """True if =path/_tree_= identifies this directory as a Branch (or
    legacy bash =node=).
    """
    return FILE_TreeObject(path).isBranch()


def leafPredicate(path: typing.Union[str, pathlib.Path]) -> bool:
    """True if =path/_tree_= identifies this directory as a Leaf."""
    return FILE_TreeObject(path).isLeaf()


# Directories to skip during autodiscover. Convention borrowed from the bash
# reference: dot-directories and metadata dirs like _nodeBase_. If a caller
# needs one of these included, use explicit branchesList / leavesList.
_AUTODISCOVER_SKIP_PREFIXES = ('.', '_')


def _autoDiscoverChildren(
    basePath: pathlib.Path,
    wantedTypes: tuple[FileTreeItem, ...],
    leafProcessors: typing.Optional[list[str]] = None,
) -> list[pathlib.Path]:
    """Enumerate immediate child directories of basePath whose classification
    matches one of the wantedTypes.

    When =leafProcessors= is given, children are classified via the
    updated =nodeType()= rules (explicit marker → leaf-processor detection
    → AuxBranch default). Otherwise only children with explicit =_tree_=
    markers are considered.

    Sorted alphabetically. Skips dot- and _-prefixed directory names by
    default.
    """
    if not basePath.is_dir():
        return []
    hits: list[pathlib.Path] = []
    for child in sorted(basePath.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith(_AUTODISCOVER_SKIP_PREFIXES):
            continue
        nt = FILE_TreeObject(child).nodeType(leafProcessors=leafProcessors)
        if nt in wantedTypes:
            hits.append(child)
    return hits


def _resolveList(
    basePath: pathlib.Path,
    listed: typing.Optional[list[str]],
    excludes: typing.Optional[list[str]],
    ordered: typing.Optional[list[str]],
    autodiscover: typing.Callable[[pathlib.Path], list[pathlib.Path]],
) -> list[pathlib.Path]:
    """Common resolution order shared by effectiveBranches / effectiveLeaves.

    1. If =ordered= is given, use those names verbatim (in that order).
       Excludes are ignored --- =ordered= is authoritative.
    2. Else the candidate set is =listed= if given, or autodiscover otherwise.
       Then =excludes= is subtracted from that set. Result is sorted.

    All names in =listed=/=ordered=/=excludes= are joined against basePath.
    """
    if ordered is not None:
        return [basePath / name for name in ordered]
    if listed is not None:
        candidates = [basePath / name for name in listed]
    else:
        candidates = autodiscover(basePath)
    excludeSet = set(excludes or [])
    return sorted(
        [p for p in candidates if p.name not in excludeSet],
        key=lambda p: p.name,
    )


def effectiveBranches(
    basePath: typing.Union[str, pathlib.Path],
    branchesList: typing.Optional[list[str]] = None,
    branchesExcludes: typing.Optional[list[str]] = None,
    branchesOrdered: typing.Optional[list[str]] = None,
    leafProcessors: typing.Optional[list[str]] = None,
) -> list[pathlib.Path]:
    """Return the ordered list of effective *child* branches beneath basePath.

    Resolution:
    1. =branchesOrdered= verbatim, or
    2. =branchesList= minus =branchesExcludes= sorted, or
    3. autodiscover (children whose classification is Branch or AuxBranch;
       classification honors =leafProcessors= per =nodeType()= rules).
    """
    basePath = pathlib.Path(basePath)
    return _resolveList(
        basePath, branchesList, branchesExcludes, branchesOrdered,
        lambda p: _autoDiscoverChildren(
            p, (FileTreeItem.Branch, FileTreeItem.AuxBranch),
            leafProcessors=leafProcessors,
        ),
    )


def effectiveLeaves(
    basePath: typing.Union[str, pathlib.Path],
    leavesList: typing.Optional[list[str]] = None,
    leavesExcludes: typing.Optional[list[str]] = None,
    leavesOrdered: typing.Optional[list[str]] = None,
    leafProcessors: typing.Optional[list[str]] = None,
) -> list[pathlib.Path]:
    """Return the ordered list of effective child leaves beneath basePath.

    Same resolution shape as =effectiveBranches= but for leaves
    (autodiscover matches Leaf or AuxLeaf; leaf detection via
    =leafProcessors= applies).
    """
    basePath = pathlib.Path(basePath)
    return _resolveList(
        basePath, leavesList, leavesExcludes, leavesOrdered,
        lambda p: _autoDiscoverChildren(
            p, (FileTreeItem.Leaf, FileTreeItem.AuxLeaf),
            leafProcessors=leafProcessors,
        ),
    )


@dataclass
class WalkResult:
    """Per-walk aggregated result. One entry per node visited."""
    visited:  list[pathlib.Path]      = field(default_factory=list)
    passed:   list[pathlib.Path]      = field(default_factory=list)
    failed:   list[pathlib.Path]      = field(default_factory=list)
    skipped:  list[pathlib.Path]      = field(default_factory=list)
    errors:   dict[pathlib.Path, str] = field(default_factory=dict)


def _applyCommand(
    node: 'FILE_TreeObject',
    command: typing.Union[list[str], typing.Callable[['FILE_TreeObject'], bool]],
    leafProcessors: typing.Optional[list[str]] = None,
) -> tuple[bool, typing.Optional[str]]:
    """Apply =command= at =node=. Returns (success, errMsg).

    Two call shapes for =command=:
    - list[str] --- treat as argv; run the node's =_treeProc_= with those
      args, in the node's directory. =_treeProc_= is resolved via
      =node.treeProc(leafProcessors=...)= so implicit leaf/auxBranch
      defaults apply. If still unresolved, skip (=success=False=,
      errMsg).
    - callable --- invoke with the FILE_TreeObject. The callable's truthy
      return maps to success; falsy → failure.
    """
    if callable(command):
        try:
            ok = bool(command(node))
            return ok, None if ok else "callable returned falsy"
        except Exception as exc:
            return False, f"callable raised: {exc!r}"

    # command is a list[str]
    proc = node.treeProc(leafProcessors=leafProcessors)
    if not proc:
        return False, f"no _treeProc_ at {node.fileTreeBasePath()}"
    # Planted-copy precedence: the "spread planted" contract is that each
    # node's own copy of the executable is authoritative. Check the node
    # directory first; only fall back to PATH if the node has no local copy.
    candidate = node.fileTreeBasePath() / proc
    if candidate.is_file():
        execPath = str(candidate)
    else:
        execPath = shutil.which(proc)
        if execPath is None:
            return False, f"_treeProc_ {proc!r} not found in {node.fileTreeBasePath()} or on PATH"
    try:
        result = subprocess.run(
            [execPath, *command],
            cwd=str(node.fileTreeBasePath()),
            check=False,
        )
    except FileNotFoundError as exc:
        return False, f"exec failed: {exc}"
    return result.returncode == 0, None if result.returncode == 0 else f"exit={result.returncode}"


_LEAFPROCS_SENTINEL: list = []  # module-level sentinel for "unset" leafProcessors


# Uniform sub-branch dispatcher filename. When the walker enters a
# sub-branch and =subBranchArgv= is set, it invokes exactly this file at
# the sub-branch dir as a subprocess.
BRANCH_SPCS_FILENAME = 'ftoBranchProc.spcs'


def treeRecurse(
    basePath: typing.Union[str, pathlib.Path],
    command: typing.Union[list[str], typing.Callable[[FILE_TreeObject], bool]],
    applyAtBranch: bool = True,
    applyAtLeaf: bool = True,
    skipSymlinks: bool = True,
    branchesList: typing.Optional[list[str]] = None,
    branchesExcludes: typing.Optional[list[str]] = None,
    branchesOrdered: typing.Optional[list[str]] = None,
    leavesList: typing.Optional[list[str]] = None,
    leavesExcludes: typing.Optional[list[str]] = None,
    leavesOrdered: typing.Optional[list[str]] = None,
    leafProcessors: typing.Optional[list[str]] = _LEAFPROCS_SENTINEL,
    subBranchArgv: typing.Optional[list[str]] = None,
    result: typing.Optional[WalkResult] = None,
    _visited: typing.Optional[set[pathlib.Path]] = None,
) -> WalkResult:
    """Walk the tree rooted at basePath, applying =command= at each node.

    =command= can be either:
    - A list[str] (argv). Applied by invoking the node's =_treeProc_= with
      those args, in the node's directory.
    - A callable. Called with the node's =FILE_TreeObject=. Return True for
      pass, False for fail.

    Semantics (matches vis_treeRecurse in lcnObjectTree.libSh):
    - Ignore     → skip whole subtree.
    - Branch     → apply command (if =applyAtBranch=), then walk
                   effectiveLeaves, then recurse into effectiveBranches.
    - AuxBranch  → recurse (do not apply here).
    - Leaf       → apply command (if =applyAtLeaf=).
    - AuxLeaf    → skip application, do not error.
    - Symlink branches → skip (cycle avoidance) when =skipSymlinks= is True.

    Continues on failure. Returns a =WalkResult= aggregating per-node
    outcomes *for this walk frame only* --- when =subBranchArgv= triggers
    subprocess dispatch into a sub-branch, that sub-branch's WalkResult
    stays with its subprocess and is NOT merged into this one. See the
    =subBranchArgv= discussion below.

    Membership overrides (=branchesList=, =leavesList=, etc.) apply to
    the *current* invocation only. Recursed sub-branches autodiscover
    unless they carry their own overrides via their own =.spcs= module.

    *Sub-branch dispatch mode:*

    - =subBranchArgv=None= (default) --- In-process recursion into
      sub-branches. Fast, singleton is shared across levels, one
      WalkResult aggregates the entire subtree. Correct only when the
      whole subtree is *homogeneous* (same domain seed, same
      =leafProcessors=).

    - =subBranchArgv=[...]= --- Subprocess dispatch. When the walker
      finds a sub-branch that contains its own =ftoBranchProc.spcs=, it
      invokes =./ftoBranchProc.spcs= with =subBranchArgv= as arguments
      as a subprocess (cwd = sub-branch dir). That sub-branch re-runs
      its own =.spcs=, re-establishes its own singleton, and does its
      own walk. Results stream to the subprocess's stdout; the parent
      does NOT merge them. Correct for *heterogeneous* trees where each
      sub-branch may declare its own domain, leafProcessors, etc. A
      sub-branch without its own =ftoBranchProc.spcs= silently falls
      back to in-process recursion (Deliverable 5's implicit auxBranch:
      the sub-branch is content the current walk owns).

    Cmnds =fto_forwardToLeaves= and =fto_walkRunExternal= expose a
    =recurseMode= CS parameter (=subprocess= (default) / =inProcess=)
    that maps to whether they pass a =subBranchArgv=.
    """
    basePath = pathlib.Path(basePath).resolve()
    if result is None:
        result = WalkResult()
    if _visited is None:
        _visited = set()

    # Resolve leafProcessors: if caller passed something (including
    # explicit None or []), honor it. If sentinel is still in place, try
    # the singleton from ftoBranch_seedInfo. Fall back to None (legacy
    # behavior: only explicit markers are recognized).
    if leafProcessors is _LEAFPROCS_SENTINEL:
        try:
            from bisos.fileObj.ftoBranch_seedInfo import ftoBranchSeedInfo
            leafProcessors = ftoBranchSeedInfo.leafProcessors
        except Exception:
            leafProcessors = None

    # Cycle safety --- do not revisit paths.
    if basePath in _visited:
        result.skipped.append(basePath)
        return result
    _visited.add(basePath)

    result.visited.append(basePath)

    node = FILE_TreeObject(basePath)
    nt = node.nodeType(leafProcessors=leafProcessors)

    if nt == FileTreeItem.Ignore:
        result.skipped.append(basePath)
        return result

    # Apply-at-here for Branch or Leaf (not Aux variants, not unmarked).
    if nt == FileTreeItem.Branch and applyAtBranch:
        ok, err = _applyCommand(node, command, leafProcessors=leafProcessors)
        (result.passed if ok else result.failed).append(basePath)
        if err:
            result.errors[basePath] = err
    elif nt == FileTreeItem.Leaf and applyAtLeaf:
        ok, err = _applyCommand(node, command, leafProcessors=leafProcessors)
        (result.passed if ok else result.failed).append(basePath)
        if err:
            result.errors[basePath] = err
        # Leaves have no children by definition. Nothing further to walk.
        return result
    elif nt == FileTreeItem.AuxLeaf:
        # Skip application; leaves have no children.
        result.skipped.append(basePath)
        return result
    elif nt is None:
        # No marker AND no leafProcessors context --- treat as an
        # unclassified branch: don't apply, but still recurse (matches
        # bash behavior for tree roots without their own _tree_ marker).
        pass
    # AuxBranch falls through to the recurse block.

    # Walk this branch's effective leaves.
    for leafPath in effectiveLeaves(
        basePath, leavesList, leavesExcludes, leavesOrdered,
        leafProcessors=leafProcessors,
    ):
        if skipSymlinks and leafPath.is_symlink():
            result.skipped.append(leafPath)
            continue
        leafNode = FILE_TreeObject(leafPath)
        leafType = leafNode.nodeType(leafProcessors=leafProcessors)
        result.visited.append(leafPath)
        if leafType == FileTreeItem.Ignore or leafType == FileTreeItem.AuxLeaf:
            result.skipped.append(leafPath)
            continue
        if applyAtLeaf:
            ok, err = _applyCommand(leafNode, command, leafProcessors=leafProcessors)
            (result.passed if ok else result.failed).append(leafPath)
            if err:
                result.errors[leafPath] = err

    # Recurse into effective sub-branches.
    for branchPath in effectiveBranches(
        basePath, branchesList, branchesExcludes, branchesOrdered,
        leafProcessors=leafProcessors,
    ):
        if skipSymlinks and branchPath.is_symlink():
            result.skipped.append(branchPath)
            continue

        # Subprocess dispatch: if =subBranchArgv= is set AND this sub-branch
        # has its own ftoBranchProc.spcs, hand off to it. The sub-branch
        # subprocess re-establishes its own domain context (leafProcessors,
        # leafExamples, etc.) from its own .spcs. Its results stay with
        # that subprocess --- no merging into this WalkResult.
        subSpcs = branchPath / BRANCH_SPCS_FILENAME
        if subBranchArgv is not None and subSpcs.is_file():
            # Record the fact of dispatch in the parent WalkResult so the
            # walker's own accounting shows "we handed off here" without
            # trying to represent the sub-tree's outcomes.
            result.visited.append(branchPath)
            try:
                proc = subprocess.run(
                    [str(subSpcs), *subBranchArgv],
                    cwd=str(branchPath),
                    check=False,
                )
                if proc.returncode == 0:
                    result.passed.append(branchPath)
                else:
                    result.failed.append(branchPath)
                    result.errors[branchPath] = f"sub-branch exit={proc.returncode}"
            except Exception as exc:
                result.failed.append(branchPath)
                result.errors[branchPath] = f"sub-branch subprocess raised: {exc!r}"
            continue

        # In-process recursion (either subBranchArgv is None OR this
        # sub-branch has no ftoBranchProc.spcs of its own --- treat as
        # implicit auxBranch content owned by the current walk).
        treeRecurse(
            branchPath,
            command,
            applyAtBranch=applyAtBranch,
            applyAtLeaf=applyAtLeaf,
            skipSymlinks=skipSymlinks,
            leafProcessors=leafProcessors,
            subBranchArgv=subBranchArgv,
            result=result,
            _visited=_visited,
        )

    return result


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
""" #+begin_org
* [[elisp:(org-cycle)][| *End-Of-Editable-Text* |]] :: emacs and org variables and control parameters
#+end_org """

### local variables:
### no-byte-compile: t
### end:
####+END:
