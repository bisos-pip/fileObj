# -*- coding: utf-8 -*-

""" #+begin_org
* ~[Summary]~ :: A =CS-Unit= with the generic lifecycle verbs, leaf side:
  =fto_prepare= ... =fto_status=, and the gate commands. A consumer leaf seed
  adds this module to its =csuList= and registers its actions with
  =ftoLeaf_seedInfo.setup()=.
#+end_org """

####+BEGIN: b:py3:cs:file/dblockControls :classification "cs-lib"
####+END:

####+BEGIN: b:prog:file/proclamations :outLevel 1
####+END:

####+BEGIN: b:prog:file/particulars :authors ("./inserts/authors-mb.org")
####+END:

if 'csInfo' not in globals(): import typing ; csInfo: typing.Dict[str, typing.Any] = { 'moduleName': ['loadAs'], }
csInfo['version'] = '202610260001'
csInfo['status']  = 'inDev'

""" #+begin_org
* [[elisp:(org-cycle)][| ~Description~ |]] :: The =fto_*= leaf verbs.
Design: README.org, "Generic Lifecycle Verbs". Each verb gates on the leaf's
=<plantStem>.control=, runs the action the consumer registered (or answers
"unsupported"), and appends a line to =<plantStem>.status=; the gating rules and
the base classes are in =ftoLeaf_seedInfo=.

Every command here is a plain top-level class and a *direct* subclass of
=cs.Cmnd= (shared behaviour comes from a mixin listed first): PyCS dispatches
only names that are both --- see =ftoLeaf_seedInfo='s description.

At a *branch*, the same names walk: =fto_csu= has branch-side =fto_prepare= ...
which forward to every leaf below (a different seed, a different process).
** Status: In development
#+end_org """

####+BEGIN: b:prog:file/orgTopControls :outLevel 1
####+END:

import typing

from bisos import b
from bisos.b import cs
from bisos.b import b_io

from bisos.fileObj import ftoLeaf_seedInfo
from bisos.fileObj.ftoLeaf_seedInfo import ControlState


def commonParamsSpecify(
        csParams: cs.param.CmndParamDict,
) -> None:
    """No parameters of its own."""
    pass


###############################################################################
# The lifecycle verbs
###############################################################################

class fto_prepare(ftoLeaf_seedInfo.LifecycleVerbMixin, cs.Cmnd):
    """Make ready to run: non-destructive, idempotent. Runs unless the leaf is disabled."""
    _verb = 'prepare'


class fto_materialize(ftoLeaf_seedInfo.LifecycleVerbMixin, cs.Cmnd):
    """Bring to the running state (idempotent). Runs only if the leaf is enabled."""
    _verb = 'materialize'


class fto_reMaterialize(ftoLeaf_seedInfo.LifecycleVerbMixin, cs.Cmnd):
    """Re-create with the current preparation; the consumer decides whether there is
    anything to do (e.g. only a stale instance). Runs only if the leaf is enabled."""
    _verb = 'reMaterialize'


class fto_unMaterialize(ftoLeaf_seedInfo.LifecycleVerbMixin, cs.Cmnd):
    """Take the running state down; the preparation is kept. Runs only if the leaf is enabled."""
    _verb = 'unMaterialize'


class fto_clean(ftoLeaf_seedInfo.LifecycleVerbMixin, cs.Cmnd):
    """Undo prepare. Runs only if the leaf is enabled."""
    _verb = 'clean'


class fto_verify(ftoLeaf_seedInfo.LifecycleVerbMixin, cs.Cmnd):
    """Check that the leaf is as it should be (read-only). Runs unless the leaf is disabled."""
    _verb = 'verify'


class fto_status(ftoLeaf_seedInfo.LifecycleVerbMixin, cs.Cmnd):
    """Show the leaf's current state (read-only, not logged). Runs unless the leaf is disabled."""
    _verb = 'status'


###############################################################################
# The gate commands --- always run
###############################################################################

class fto_enable(ftoLeaf_seedInfo.GateSetMixin, cs.Cmnd):
    """Set the leaf's gate to 'enabled': every verb runs."""
    _state = ControlState.Enabled


class fto_available(ftoLeaf_seedInfo.GateSetMixin, cs.Cmnd):
    """Set the leaf's gate to 'available' (the default): only prepare, verify and status run."""
    _state = ControlState.Available


class fto_disable(ftoLeaf_seedInfo.GateSetMixin, cs.Cmnd):
    """Set the leaf's gate to 'disabled': leave the leaf completely alone."""
    _state = ControlState.Disabled


class fto_control(cs.Cmnd):
    """Show the leaf's gate (enabled | available | disabled; no file = available)."""
    cmndParamsMandatory = []
    cmndParamsOptional = []
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        """Read the gate file."""
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        state = ftoLeaf_seedInfo.controlRead()
        path = ftoLeaf_seedInfo.controlPath()
        b_io.ann.write(f"{path.parent.name}: control={state.value}"
                       + ("" if path.is_file() else "  (no gate file: default)"))
        return cmndOutcome.set(opError=b.op.OpError.Success, opResults=state.value)


class fto_statusLog(cs.Cmnd):
    """Show the leaf's status log."""
    cmndParamsMandatory = []
    cmndParamsOptional = []
    cmndArgsLen = {'Min': 0, 'Max': 0}

    @cs.track(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(
        self,
        rtInv: cs.RtInvoker,
        cmndOutcome: b.op.Outcome,
        argsList: typing.Optional[list[str]] = None,
    ) -> b.op.Outcome:
        """Print the status log."""
        callParamsDict = {}
        if self.invocationValidate(rtInv, cmndOutcome, callParamsDict, argsList).isProblematic():
            return b_io.eh.badOutcome(cmndOutcome)
        path = ftoLeaf_seedInfo.statusPath()
        log = ftoLeaf_seedInfo.statusRead()
        b_io.ann.write(f"== {path.parent.name}: {path}")
        b_io.ann.write(log.rstrip() if log else "(empty)")
        return cmndOutcome.set(opError=b.op.OpError.Success, opResults=log)


####+BEGIN: b:py3:cs:framework/endOfFile :basedOn "classification"
####+END:
