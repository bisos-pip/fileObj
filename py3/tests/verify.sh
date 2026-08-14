#!/bin/bash -i
#
# Smoke tests for bisos.fileObj:
#   1) Library-level: import + FileTreeItem + FILE_TreeObject + walker.
#   2) Branch .spcs end-to-end (Stage 1 introspection):
#        Test 1: fto_nodeInfo reports _tree_ = Branch at the planted branch.
#        Test 2: fto_effectiveLeaves lists both leaves.
#   3) Branch .spcs end-to-end (Stage 2 forwarding + walks + hooks):
#        Test 3: fto_forwardToLeaves --cmndName=X invokes each leaf's
#                _treeProc_ -i X; leaf markers prove both leaves ran.
#        Test 4: fto_walkRunExternal runs an external cmnd at the branch
#                and both leaves (touch markers everywhere).
#        Test 5: fto_walkRunExternal with a nonexistent cmnd skips all
#                would-be apply sites (perhapsRun semantics).
#        Test 6: examplesFuncsList hook --- a .spcs that declares
#                ftoBranch_seedInfo.setup(examplesFuncsList=[...]) adds
#                its own chapter to the bare examples menu.
#        Test 7: leavesExcludes override --- a .spcs that declares
#                ftoBranch_seedInfo.setup(leavesExcludes=['leafTwo'])
#                causes fto_forwardToLeaves to skip leafTwo.
#        Test 8: leafExamples typed data --- a .spcs that declares
#                setup(leafExamples=[WalkExampleSpec(...)]) renders a
#                proper "Leaf-Provided Walk Examples" chapter, one
#                cmnd() entry per spec.
#
# Requires: bisos.fileObj pip-installed (editable is fine).

# Safety check: must run from a directory named "tests"
if [[ "$(basename "$PWD")" != "tests" ]]; then
    echo "ERROR: verify.sh must be run from a directory named 'tests'." >&2
    echo "  Current PWD: $PWD" >&2
    exit 1
fi

# =====================================================================
# Library-level smoke test (pure Python; no scratch tree yet)
# =====================================================================

lpDo python3 -c "
from bisos.fileObj import fto

# 1. All expected symbols exist.
expected = ['FileTreeItem', 'FILE_TreeObject',
            'branchPredicate', 'leafPredicate',
            'effectiveBranches', 'effectiveLeaves',
            'treeRecurse', 'WalkResult',
            'TREE_MARKER_FILE', 'TREE_PROC_FILE', 'TREE_OBJECT_TYPE_FILE']
missing = [n for n in expected if not hasattr(fto, n)]
if missing:
    print(f'  [FAIL] missing symbols: {missing}')
    import sys; sys.exit(1)
print(f'  [PASS] All {len(expected)} expected symbols present.')

# 2. FileTreeItem members.
members = [m.name for m in fto.FileTreeItem]
wanted = ['Branch', 'Leaf', 'AuxBranch', 'AuxLeaf', 'Ignore']
if sorted(members) != sorted(wanted):
    print(f'  [FAIL] FileTreeItem members: got {members}, want {wanted}')
    import sys; sys.exit(1)
print(f'  [PASS] FileTreeItem members: {members}')

# 3. fromString: new vocabulary.
for s, expected in [('branch', fto.FileTreeItem.Branch),
                    ('leaf', fto.FileTreeItem.Leaf),
                    ('auxBranch', fto.FileTreeItem.AuxBranch),
                    ('auxLeaf', fto.FileTreeItem.AuxLeaf),
                    ('ignore', fto.FileTreeItem.Ignore)]:
    got = fto.FileTreeItem.fromString(s)
    status = 'PASS' if got == expected else 'FAIL'
    print(f'  [{status}] fromString({s!r}) -> {got.name}')
    if got != expected: import sys; sys.exit(1)

# 4. fromString: bash backward-compat.
for s, expected in [('node', fto.FileTreeItem.Branch),
                    ('auxNode', fto.FileTreeItem.AuxBranch),
                    ('ignoreNode', fto.FileTreeItem.AuxBranch),
                    ('ignoreLeaf', fto.FileTreeItem.AuxLeaf)]:
    got = fto.FileTreeItem.fromString(s)
    status = 'PASS' if got == expected else 'FAIL'
    print(f'  [{status}] fromString({s!r}) [bash compat] -> {got.name}')
    if got != expected: import sys; sys.exit(1)
"

# =====================================================================
# Scratch tree + walker end-to-end
# =====================================================================

lpDo python3 -c "
import tempfile
import pathlib
import subprocess
from bisos.fileObj import fto

with tempfile.TemporaryDirectory() as td:
    base = pathlib.Path(td) / 'tree'

    # Layout:
    #   base/                (branch)
    #     leaf1/             (leaf)
    #     leaf2/             (leaf)
    #     sub/               (branch)
    #       leaf3/           (leaf)
    #     auxb/              (auxBranch: traverse but do not apply)
    #       leafA/           (leaf)
    #     auxl/              (auxLeaf: skip application)
    #     ignoreme/          (ignore: whole subtree skipped)
    #       leafIgn/         (leaf --- should NOT be visited)

    fto.FILE_TreeObject(base).branchCreate(treeProc='echo')
    for name in ('leaf1', 'leaf2'):
        fto.FILE_TreeObject(base / name).leafCreate(treeProc='echo')
    fto.FILE_TreeObject(base / 'sub').branchCreate(treeProc='echo')
    fto.FILE_TreeObject(base / 'sub' / 'leaf3').leafCreate(treeProc='echo')
    fto.FILE_TreeObject(base / 'auxb').auxBranchCreate()
    fto.FILE_TreeObject(base / 'auxb' / 'leafA').leafCreate(treeProc='echo')
    fto.FILE_TreeObject(base / 'auxl').auxLeafCreate()
    fto.FILE_TreeObject(base / 'ignoreme').ignoreCreate()
    fto.FILE_TreeObject(base / 'ignoreme' / 'leafIgn').leafCreate(treeProc='echo')

    # --- predicates ---
    print(f'  [PASS] branchPredicate on base:     {fto.branchPredicate(base)}')
    print(f'  [PASS] leafPredicate on leaf1:      {fto.leafPredicate(base / \"leaf1\")}')
    print(f'  [PASS] leafPredicate on base:       {not fto.leafPredicate(base)}')

    # --- effectiveBranches / effectiveLeaves ---
    branches = fto.effectiveBranches(base)
    leaves   = fto.effectiveLeaves(base)
    bnames = sorted(p.name for p in branches)
    lnames = sorted(p.name for p in leaves)
    # base's immediate leaves: leaf1, leaf2. auxl is AuxLeaf -> also autodiscovered.
    # base's immediate branches: sub, auxb.
    assert 'leaf1' in lnames and 'leaf2' in lnames and 'auxl' in lnames, f'leaves: {lnames}'
    assert 'sub' in bnames and 'auxb' in bnames, f'branches: {bnames}'
    print(f'  [PASS] effectiveBranches(base): {bnames}')
    print(f'  [PASS] effectiveLeaves(base):   {lnames}')

    # --- bash backward-compat read ---
    (base / 'bashSub').mkdir()
    (base / 'bashSub' / '_tree_').write_text('node\n')     # bash vocabulary
    (base / 'bashSub' / '_treeProc_').write_text('echo\n')
    print(f'  [PASS] bash \"node\" read as Branch: '
          f'{fto.FILE_TreeObject(base / \"bashSub\").nodeType().name}')
    print(f'  [PASS] bash \"node\" branchPredicate: '
          f'{fto.branchPredicate(base / \"bashSub\")}')

    # --- walker: callable form (in-process, no subprocess needed) ---
    visited = []
    def collect(node):
        visited.append(node.fileTreeBasePath().name)
        return True
    result = fto.treeRecurse(base, collect)

    print(f'  [PASS] walker visited count: {len(result.visited)}')
    # Expected passes: leaf1, leaf2, sub, leaf3 (under sub), leafA (under auxb).
    # Skipped: auxl, ignoreme (whole subtree), auxb (branch itself, no apply).
    # The base branch itself IS applied (Branch and applyAtBranch=True by default).
    assert 'leaf1' in visited, visited
    assert 'leaf2' in visited, visited
    assert 'leaf3' in visited, visited
    assert 'leafA' in visited, visited
    assert 'leafIgn' not in visited, f'leafIgn should be skipped (parent is ignore): {visited}'
    print(f'  [PASS] walker respected ignore (leafIgn not visited)')
    print(f'  [PASS] walker respected auxBranch (leafA reached via auxb)')

    # --- cycle safety: symlink to self ---
    (base / 'sub' / 'cycle').symlink_to(base)
    visited2 = []
    def collect2(node):
        visited2.append(str(node.fileTreeBasePath()))
        return True
    result2 = fto.treeRecurse(base, collect2)
    # Should terminate; symlink branches are skipped.
    print(f'  [PASS] walker survived a symlink cycle (visited={len(result2.visited)})')
"

# =====================================================================
# Branch .spcs end-to-end
# =====================================================================
# Build a scratch tree with ftoBranchProc.spcs at the branch and two
# leaves. Verify:
#   (a) -i fto_nodeInfo runs against the planted branch and reports
#       _tree_ = Branch.
#   (b) -i fto_effectiveLeaves lists the two leaves.

lpDo bash -c '
set -e
scratch=$(mktemp -d)
trap "rm -rf $scratch" EXIT

branch="$scratch/branchA"
mkdir -p "$branch"
echo branch > "$branch/_tree_"
cp ../bin/ftoBranchProc.spcs "$branch/ftoBranchProc.spcs"
chmod +x "$branch/ftoBranchProc.spcs"
echo "ftoBranchProc.spcs" > "$branch/_treeProc_"

for name in leafOne leafTwo; do
    dir="$branch/$name"
    mkdir -p "$dir"
    echo leaf > "$dir/_tree_"
done

echo ""
echo "=== Scratch tree ==="
find "$scratch" -type f -o -type d | head -20
echo ""

echo "=== Test 1: fto_nodeInfo at branch (local dispatch) ==="
cd "$branch"
nodeInfoOut=$(./ftoBranchProc.spcs -i fto_nodeInfo 2>&1)
echo "$nodeInfoOut"
if echo "$nodeInfoOut" | grep -q "_tree_.*Branch"; then
    echo "  [PASS] fto_nodeInfo reported _tree_ = Branch"
else
    echo "  [FAIL] fto_nodeInfo did not report Branch"
fi
echo ""

echo "=== Test 2: fto_effectiveLeaves at branch ==="
leavesOut=$(./ftoBranchProc.spcs -i fto_effectiveLeaves 2>&1)
echo "$leavesOut"
if echo "$leavesOut" | grep -q "leafOne" && echo "$leavesOut" | grep -q "leafTwo"; then
    echo "  [PASS] fto_effectiveLeaves listed both leaves"
else
    echo "  [FAIL] fto_effectiveLeaves did not list both leaves"
fi
echo ""

# =====================================================================
# Stage 2: forwarding + walks + hooks
# =====================================================================
# Give each leaf a bash _treeProc_ named "leafProc.sh" that writes a
# marker recording its cwd and args. This lets us verify both
# fto_forwardToLeaves (Mode 1) and fto_walkRunExternal (Mode 2).

for name in leafOne leafTwo; do
    dir="$branch/$name"
    proc="$dir/leafProc.sh"
    cat > "$proc" <<SCRIPT
#!/bin/bash
echo "\$(pwd) called with: \$@" >> "$scratch/callLog"
SCRIPT
    chmod +x "$proc"
    echo "leafProc.sh" > "$dir/_treeProc_"
done

echo "=== Test 3: fto_forwardToLeaves --cmndName=someVerb ==="
> "$scratch/callLog"
./ftoBranchProc.spcs -i fto_forwardToLeaves --cmndName=someVerb 2>&1 | tail -12
echo "--- callLog ---"
if [[ -f "$scratch/callLog" ]] ; then cat "$scratch/callLog" ; fi
numCalls=$(wc -l < "$scratch/callLog" 2>/dev/null || echo 0)
if [[ "$numCalls" == "2" ]] ; then
    echo "  [PASS] fto_forwardToLeaves invoked both leaves (numCalls=$numCalls)"
else
    echo "  [FAIL] Expected 2 leaf calls, got $numCalls"
fi
echo ""

echo "=== Test 4: fto_walkRunExternal touch <marker> ==="
# Use a per-node absolute marker so we can inspect what ran where.
# touch is in PATH, so it should run at branch + both leaves = 3 places.
rm -f "$branch"/marker.txt "$branch"/leafOne/marker.txt "$branch"/leafTwo/marker.txt
./ftoBranchProc.spcs -i fto_walkRunExternal touch marker.txt 2>&1 | tail -12
markerCount=0
for f in "$branch/marker.txt" "$branch/leafOne/marker.txt" "$branch/leafTwo/marker.txt" ; do
    [[ -f "$f" ]] && markerCount=$((markerCount+1))
done
if [[ "$markerCount" == "3" ]] ; then
    echo "  [PASS] fto_walkRunExternal ran at branch + both leaves ($markerCount markers)"
else
    echo "  [FAIL] Expected 3 markers (branch + 2 leaves), got $markerCount"
fi
echo ""

echo "=== Test 5: fto_walkRunExternal <nonexistent-cmnd> (perhapsRun skip) ==="
# This scratch tree has branch + 2 direct leaves (no auxBranches), so
# all 3 nodes are apply-eligible; all 3 get skipped.
skipOut=$(./ftoBranchProc.spcs -i fto_walkRunExternal thisCmndDoesNotExist 2>&1)
echo "$skipOut" | tail -6
if echo "$skipOut" | grep -q "cmnd-skip=3" ; then
    echo "  [PASS] perhapsRun skipped 3 would-be apply sites (branch + 2 leaves)"
else
    echo "  [FAIL] Expected cmnd-skip=3 in output"
fi
'

# =====================================================================
# Tests 6 and 7: examplesFuncsList hook + leavesExcludes override
# =====================================================================
# We write the custom .spcs to a temp file OUTSIDE the bash -c '...' block
# because the .spcs body contains many literal single quotes (Python
# strings) that would break the outer single-quoted argument.

customSpcs=$(mktemp --suffix=.spcs)
cat > "$customSpcs" << 'EOF_SPCS'
#!/usr/bin/env python
from bisos.b import cs
from bisos.fileObj import ftoBranch_seed  # noqa: F401  _atExit_
from bisos.fileObj import ftoBranch_seedInfo

def myDomainExamples():
    cs.examples.menuChapter('=Hook Test Chapter=')
    cs.examples.execInsert("# HOOK MARKER STRING")

ftoBranch_seedInfo.setup(
    examplesFuncsList=[myDomainExamples],
    leavesExcludes=['leafTwo'],
)

def examples_pcs() -> None:
    pass
EOF_SPCS

lpDo bash -c "
set -e
scratch=\$(mktemp -d)
trap 'rm -rf \$scratch' EXIT

branch=\"\$scratch/branchA\"
mkdir -p \"\$branch\"
echo branch > \"\$branch/_tree_\"
cp \"$customSpcs\" \"\$branch/ftoBranchProc.spcs\"
chmod +x \"\$branch/ftoBranchProc.spcs\"
echo ftoBranchProc.spcs > \"\$branch/_treeProc_\"

for name in leafOne leafTwo ; do
    dir=\"\$branch/\$name\"
    mkdir -p \"\$dir\"
    echo leaf > \"\$dir/_tree_\"
    proc=\"\$dir/leafProc.sh\"
    printf '%s\n%s\n' '#!/bin/bash' 'echo \"\$(pwd) called with: \$@\" >> '\"\$scratch\"'/callLog' > \"\$proc\"
    chmod +x \"\$proc\"
    echo leafProc.sh > \"\$dir/_treeProc_\"
done

cd \"\$branch\"

echo '=== Test 6: examplesFuncsList hook adds a chapter ==='
menuOut=\$(./ftoBranchProc.spcs 2>&1)
if echo \"\$menuOut\" | grep -q '=Hook Test Chapter=' && echo \"\$menuOut\" | grep -q 'HOOK MARKER STRING' ; then
    echo '  [PASS] examplesFuncsList hook produced its chapter in the menu'
else
    echo '  [FAIL] Hook chapter not found in menu output'
    echo '--- last 40 lines of menu output ---'
    echo \"\$menuOut\" | tail -40
fi
echo ''

echo \"=== Test 7: leavesExcludes=[leafTwo] override skips leafTwo ===\"
> \"\$scratch/callLog\"
./ftoBranchProc.spcs -i fto_forwardToLeaves --cmndName=someVerb 2>&1 | tail -8
echo '--- callLog after override ---'
if [[ -f \"\$scratch/callLog\" ]] ; then cat \"\$scratch/callLog\" ; fi
if grep -q leafOne \"\$scratch/callLog\" 2>/dev/null && ! grep -q leafTwo \"\$scratch/callLog\" 2>/dev/null ; then
    echo '  [PASS] leavesExcludes skipped leafTwo (leafOne ran, leafTwo did not)'
else
    echo '  [FAIL] leavesExcludes did not honor the exclusion'
fi
"
rm -f "$customSpcs"

# =====================================================================
# Test 8: leafExamples typed data renders proper cmnd() entries
# =====================================================================
# Custom .spcs declares leafExamples=[WalkExampleSpec(...), ...] via setup().
# Verifies the menu contains a "Leaf-Provided Walk Examples" chapter and
# each spec's cmndName + comment shows up in the output.

customSpcs8=$(mktemp --suffix=.spcs)
cat > "$customSpcs8" << 'EOF_SPCS'
#!/usr/bin/env python
from bisos.fileObj import ftoBranch_seed  # noqa: F401  _atExit_
from bisos.fileObj import ftoBranch_seedInfo
from bisos.fileObj.ftoBranch_seedInfo import WalkExampleSpec

ftoBranch_seedInfo.setup(
    leafExamples=[
        WalkExampleSpec(cmndName='typedSpecOne',
                        comment="# spec-one-comment-marker"),
        WalkExampleSpec(cmndName='typedSpecTwo',
                        pars={'foo': 'bar'},
                        comment="# spec-two-comment-marker"),
        WalkExampleSpec(cmndName='typedSpecExternal',
                        args='--flag=x',
                        mode='walkRunExternal',
                        comment="# spec-external-comment-marker"),
    ],
)

def examples_pcs() -> None:
    pass
EOF_SPCS

lpDo bash -c "
set -e
scratch=\$(mktemp -d)
trap 'rm -rf \$scratch' EXIT

branch=\"\$scratch/branchA\"
mkdir -p \"\$branch\"
echo branch > \"\$branch/_tree_\"
cp \"$customSpcs8\" \"\$branch/ftoBranchProc.spcs\"
chmod +x \"\$branch/ftoBranchProc.spcs\"
echo ftoBranchProc.spcs > \"\$branch/_treeProc_\"

cd \"\$branch\"

echo '=== Test 8: leafExamples typed data ==='
menuOut=\$(./ftoBranchProc.spcs 2>&1)

pass=1
for token in \\
    '=Leaf-Provided Walk Examples (Mode 1)=' \\
    '=Leaf-Provided Walk Examples (Mode 2)=' \\
    typedSpecOne \\
    typedSpecTwo \\
    typedSpecExternal \\
    spec-one-comment-marker \\
    spec-two-comment-marker \\
    spec-external-comment-marker \\
    --foo=\\\"bar\\\" ; do
    if ! echo \"\$menuOut\" | grep -qF -- \"\$token\" ; then
        echo \"  MISSING: \$token\"
        pass=0
    fi
done

if [[ \"\$pass\" == \"1\" ]] ; then
    echo '  [PASS] leafExamples rendered Mode-1 + Mode-2 chapters and all specs'
else
    echo '  [FAIL] leafExamples did not render everything'
    echo '--- last 40 lines of menu output ---'
    echo \"\$menuOut\" | tail -40
fi
"
rm -f "$customSpcs8"
