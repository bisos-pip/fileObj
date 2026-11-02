# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: Leaf side of the generic lifecycle verbs --- the gate, the
  status log, and the registration of a consumer's actions. Used by
  =ftoLeaf_csu= (the =fto_*= leaf verbs) and by consumer leaf seeds.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-u"
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
####+END:

if 'csInfo' not in globals(): import typing ; csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['loadAs'], }
csInfo['version'] = '202610260001'
csInfo['status']  = 'inDev'

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: The generic lifecycle verbs, leaf side.
Design: README.org, "Generic Lifecycle Verbs". In short:

- Seven verbs: =fto_prepare=, =fto_materialize=, =fto_reMaterialize=,
  =fto_unMaterialize=, =fto_clean=, =fto_verify=, =fto_status=. A consumer
  registers what each does for its kind of leaf with =setup()=; a verb it does
  not register is "unsupported" at that leaf kind (success, logged).
- The gate, =<leaf>/<plantStem>.control=: =enabled= | =available= |
  =disabled=; missing = =available=.
  - =disabled= --- leave this leaf completely alone: every verb skips.
  - =available= --- =prepare=, =verify= and =status= run; the destructive
    verbs (=materialize=, =reMaterialize=, =unMaterialize=, =clean=) skip.
  - =enabled= --- every verb runs.
  The gate commands themselves (=fto_enable= ...) always run.
- The status log, =<leaf>/<plantStem>.status=: one timestamped line per run
  (=fto_status= is not logged). The same files and formats as CBM's
  =cbmProc.control= / =cbmProc.status=.

The shared behaviour of the leaf verbs is in mixins here (=LifecycleVerbMixin=,
=GateSetMixin=), which are *not* =cs.Cmnd= subclasses: PyCS dispatches only
names that are top-level classes in a =csuList= module's source *and* direct
subclasses of =cs.Cmnd= (=bisos.b.cs.inCmnd.cmndList_mainsMethods= intersects the
scanned names with =cs.cmndSubclassesNames()=, i.e. =cs.Cmnd.__subclasses__()=).
So each command is declared =class fto_x(LifecycleVerbMixin, cs.Cmnd)=; a class
deriving from another command class would never be dispatched.
** Status: In development
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
####+END:

import datetime
import enum
import pathlib
import typing
from dataclasses import dataclass, field

from bisos import b
from bisos.b import cs
from bisos.b import b_io
from bisos.csSeed import seedsLib


###############################################################################
# The verbs and how the gate treats them
###############################################################################

@enum.unique
class ControlState(enum.Enum):
    Available = "available"     # present, not activated: only non-destructive verbs run
    Enabled   = "enabled"       # every verb runs
    Disabled  = "disabled"      # leave the leaf completely alone: every verb skips


# A missing .control file: nothing destructive happens until the leaf is enabled.
DEFAULT_CONTROL = ControlState.Available


@enum.unique
class Gating(enum.Enum):
    NotDisabled = "notDisabled"   # runs unless the gate is 'disabled'
    EnabledOnly = "enabledOnly"   # runs only if the gate is 'enabled'


@dataclass(frozen=True)
class VerbSpec:
    name: str              # the registration key, e.g. 'prepare'
    cmndName: str          # the command, e.g. 'fto_prepare'
    gating: Gating
    logged: bool
    means: str             # one line, for menus


VERBS: tuple[VerbSpec, ...] = (
    VerbSpec('prepare', 'fto_prepare', Gating.NotDisabled, True,
             "make ready to run (non-destructive, idempotent)"),
    VerbSpec('materialize', 'fto_materialize', Gating.EnabledOnly, True,
             "bring to the running state (idempotent)"),
    VerbSpec('reMaterialize', 'fto_reMaterialize', Gating.EnabledOnly, True,
             "re-create with the current preparation (decides itself whether to)"),
    VerbSpec('unMaterialize', 'fto_unMaterialize', Gating.EnabledOnly, True,
             "take the running state down (preparation kept)"),
    VerbSpec('clean', 'fto_clean', Gating.EnabledOnly, True,
             "undo prepare"),
    VerbSpec('verify', 'fto_verify', Gating.NotDisabled, True,
             "check that the leaf is as it should be (read-only)"),
    VerbSpec('status', 'fto_status', Gating.NotDisabled, False,
             "show the leaf's current state (read-only)"),
)

VERB_BY_NAME = {v.name: v for v in VERBS}

GATE_CMND_NAMES = ('fto_control', 'fto_statusLog', 'fto_enable', 'fto_available', 'fto_disable')


###############################################################################
# Registration of a consumer's actions
###############################################################################

Action = typing.Callable[[b.op.Outcome], b.op.Outcome]


@dataclass
class FtoLeafSeedInfo:
    """Singleton: the actions a consumer registered, by verb name."""
    actions: dict[str, Action] = field(default_factory=dict)

    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


ftoLeafSeedInfo = FtoLeafSeedInfo()


def setup(
        prepare: typing.Optional[Action] = None,
        materialize: typing.Optional[Action] = None,
        reMaterialize: typing.Optional[Action] = None,
        unMaterialize: typing.Optional[Action] = None,
        clean: typing.Optional[Action] = None,
        verify: typing.Optional[Action] = None,
        status: typing.Optional[Action] = None,
) -> None:
    """Register what each lifecycle verb does for this kind of leaf.

    Each action is =(cmndOutcome) -> b.op.Outcome=; the consumer resolves its own
    leaf parameters (e.g. from the planted path) inside it. A verb left as None is
    "unsupported" at this leaf kind. Called by the consumer's csu module at import.
    """
    given = dict(prepare=prepare, materialize=materialize, reMaterialize=reMaterialize,
                 unMaterialize=unMaterialize, clean=clean, verify=verify, status=status)
    for name, action in given.items():
        if action is not None:
            ftoLeafSeedInfo.actions[name] = action


###############################################################################
# Gate and status log --- the CBM formats (bisos.capability.cbmProc_seedInfo)
###############################################################################

def leafPlantPath(plantPath: typing.Union[str, pathlib.Path, None] = None) -> pathlib.Path:
    """The leaf's planted file (e.g. <leaf>/dockerProc.spcs), resolved.

    A seeded leaf: the seed's plantOfThisSeed. Otherwise (a leaf whose processor is a
    plain PyCS program, not a planted .spcs): the running program itself, sys.argv[0].
    """
    import sys
    if plantPath is None:
        plantPath = seedsLib.seededCsxuInfo.plantOfThisSeed
    if plantPath is None and sys.argv and sys.argv[0] and pathlib.Path(sys.argv[0]).is_file():
        plantPath = sys.argv[0]
    if plantPath is None:
        raise ValueError("No planted file: run this from a leaf's planted .spcs")
    return pathlib.Path(plantPath).resolve()


def _gateFile(suffix: str, plantPath=None) -> pathlib.Path:
    plant = leafPlantPath(plantPath)
    return plant.parent / f"{plant.stem}.{suffix}"


def controlPath(plantPath=None) -> pathlib.Path:
    return _gateFile("control", plantPath)


def statusPath(plantPath=None) -> pathlib.Path:
    return _gateFile("status", plantPath)


def controlRead(plantPath=None) -> ControlState:
    """The leaf's gate state. Missing file or unknown content -> DEFAULT_CONTROL."""
    try:
        return ControlState(controlPath(plantPath).read_text().strip())
    except (OSError, ValueError):
        return DEFAULT_CONTROL


def controlWrite(state: ControlState, plantPath=None) -> None:
    controlPath(plantPath).write_text(f"{state.value}\n")


def statusRead(plantPath=None) -> str:
    try:
        return statusPath(plantPath).read_text()
    except OSError:
        return ""


def statusWrite(line: str, plantPath=None) -> None:
    """Append '<ISO timestamp>  <line>' to the leaf's status log."""
    stamp = datetime.datetime.now().isoformat(timespec='seconds')
    with statusPath(plantPath).open('a') as fh:
        fh.write(f"{stamp}  {line}\n")


def statusLinesSince(since: datetime.datetime, statusFile: pathlib.Path) -> list[str]:
    """The lines of a status log written at or after =since= (for branch summaries)."""
    try:
        text = statusFile.read_text()
    except OSError:
        return []
    lines = []
    for line in text.splitlines():
        stamp, _, rest = line.partition('  ')
        try:
            if datetime.datetime.fromisoformat(stamp) >= since.replace(microsecond=0):
                lines.append(rest)
        except ValueError:
            continue
    return lines


def _logStatus(line: str) -> None:
    """Append to the status log; a read-only checkout must not break the command."""
    try:
        statusWrite(line)
    except OSError as exc:
        b_io.ann.note(f"WARNING: could not write {statusPath()}: {exc}")


###############################################################################
# Mixins of the fto_* leaf verbs (see the Description: deliberately not cs.Cmnd)
###############################################################################

class LifecycleVerbMixin:
    """Gate, run the registered action (or answer 'unsupported'), log, return its outcome.

    Use as: class fto_x(LifecycleVerbMixin, cs.Cmnd): _verb = 'x'
    """
    cmndParamsMandatory = []
    cmndParamsOptional = []
    cmndArgsLen = {'Min': 0, 'Max': 0}
    _verb = ''

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        """Gate, act, log."""
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)

        spec = VERB_BY_NAME[self._verb]
        state = controlRead()
        allowed = (state == ControlState.Enabled if spec.gating == Gating.EnabledOnly
                   else state != ControlState.Disabled)
        if not allowed:
            b_io.ann.note(f"{spec.cmndName}: skipped --- control={state.value}")
            _logStatus(f"skipped: control={state.value} at {spec.cmndName}")
            return cmndOutcome.set(opError=b.op.OpError.Success,
                                   opResults=f"skipped: control={state.value}")

        action = ftoLeafSeedInfo.actions.get(self._verb)
        if action is None:
            b_io.ann.note(f"{spec.cmndName}: not supported by this leaf kind")
            if spec.logged:
                _logStatus(f"skipped: unsupported {spec.cmndName}")
            return cmndOutcome.set(opError=b.op.OpError.Success, opResults="unsupported")

        try:
            outcome = action(cmndOutcome)
        except Exception as exc:
            if spec.logged:
                _logStatus(f"failed: {spec.cmndName}: {exc}")
            raise
        if spec.logged:
            if outcome.error == b.op.OpError.Success:
                _logStatus(f"ran: {spec.cmndName} ok ({outcome.results})")
            else:
                _logStatus(f"failed: {spec.cmndName}: {outcome.results}")
        return outcome


class GateSetMixin:
    """Write the leaf's gate file; subclasses set _state. Always runs.

    Use as: class fto_enable(GateSetMixin, cs.Cmnd): _state = ControlState.Enabled
    """
    cmndParamsMandatory = []
    cmndParamsOptional = []
    cmndArgsLen = {'Min': 0, 'Max': 0}
    _state = ControlState.Available

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        """Write the gate, log the change."""
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        controlWrite(self._state)
        _logStatus(f"control={self._state.value}")
        b_io.ann.note(f"{controlPath()}: {self._state.value}")
        return cmndOutcome.set(opError=b.op.OpError.Success, opResults=self._state.value)


###############################################################################
# For consumers' menus
###############################################################################

def lifecycleWalkExamples() -> list:
    """WalkExampleSpec entries for the lifecycle verbs and gate commands.

    For a consumer's walkExamples(): append these. (At a branch, the same names also
    work directly: ./ftoBranchProc.spcs -i fto_prepare.)
    """
    from bisos.fileObj.ftoBranch_seedInfo import WalkExampleSpec
    specs = []
    for v in VERBS:
        tags = {'lifecycle'}
        if v.gating == Gating.EnabledOnly:
            tags.add('destructive')
        if v.name in ('verify', 'status'):
            tags.add('read-only')
        specs.append(WalkExampleSpec(cmndName=v.cmndName, comment=f"# {v.means}",
                                     tags=frozenset(tags)))
    specs += [
        WalkExampleSpec(cmndName='fto_control', comment="# show each leaf's gate",
                        tags=frozenset({'read-only', 'control'})),
        WalkExampleSpec(cmndName='fto_statusLog', comment="# show each leaf's status log",
                        tags=frozenset({'read-only', 'control'})),
        WalkExampleSpec(cmndName='fto_enable', comment="# every verb runs",
                        tags=frozenset({'control'})),
        WalkExampleSpec(cmndName='fto_available', comment="# only prepare / verify / status run",
                        tags=frozenset({'control'})),
        WalkExampleSpec(cmndName='fto_disable', comment="# leave the leaf completely alone",
                        tags=frozenset({'control'})),
    ]
    return specs


def lifecycleExamplesMenu() -> None:
    """A menu section with the verbs and gate commands, for a consumer leaf's examples menu."""
    cmnd = cs.examples.cmndEnter
    try:
        state = controlRead().value
    except ValueError:
        state = '?'
    cs.examples.menuSection(f'FTO Lifecycle Verbs (this leaf: control={state})')
    supported = ftoLeafSeedInfo.actions
    for v in VERBS:
        note = '' if v.name in supported else '  (unsupported at this leaf kind)'
        cmnd(v.cmndName, comment=f"# {v.means}{note}")
    cs.examples.menuSection('FTO Gate and Status Log')
    cmnd('fto_control', comment="# enabled | available | disabled (no file = available)")
    cmnd('fto_statusLog')
    cmnd('fto_enable', comment="# every verb runs")
    cmnd('fto_available', comment="# only prepare / verify / status run (the default)")
    cmnd('fto_disable', comment="# leave the leaf completely alone")


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
####+END:
