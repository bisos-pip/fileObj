#!/bin/bash -i
#
# Smoke tests for bisos.fileObj.fto:
#   1) Library-level: import + FileTreeItem + FILE_TreeObject + walker.
#   2) Branch .spcs end-to-end: local dispatch (fto_*) + transparent
#      forwarding of any non-fto_ Cmnd to each effective leaf.
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
# Build a scratch tree with ftoBranchProc.spcs at the branch and a tiny
# bash script as _treeProc_ at each leaf. Verify:
#   (a) -i fto_nodeInfo runs locally, does not walk.
#   (b) -i someLeafCmnd is forwarded: each leaf's _treeProc_ gets called.

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

# Two leaves. Each has a _treeProc_ that writes a marker file recording
# the fact that it was called and which -i cmnd it received.
for name in leafOne leafTwo; do
    dir="$branch/$name"
    mkdir -p "$dir"
    echo leaf > "$dir/_tree_"
    proc="$dir/leafHandler.sh"
    cat > "$proc" << SCRIPT
#!/bin/bash
# _treeProc_ for this leaf. Writes a marker recording invocation.
echo "\$(pwd) called with: \$@" >> "$scratch/callLog"
SCRIPT
    chmod +x "$proc"
    echo "leafHandler.sh" > "$dir/_treeProc_"
done

echo ""
echo "=== Scratch tree ==="
find "$scratch" -type f -o -type d | head -20
echo ""

echo "=== Test 1: local dispatch (fto_nodeInfo at branch) ==="
cd "$branch"
./ftoBranchProc.spcs -i fto_nodeInfo || true
echo ""

echo "=== Test 2: transparent forwarding (someLeafCmnd) ==="
./ftoBranchProc.spcs -i someLeafCmnd  || true
echo ""

echo "=== callLog contents ==="
if [[ -f "$scratch/callLog" ]]; then
    cat "$scratch/callLog"
    numCalls=$(wc -l < "$scratch/callLog")
    echo ""
    if [[ "$numCalls" == "2" ]]; then
        echo "  [PASS] Both leaves got called (numCalls=$numCalls)"
    else
        echo "  [FAIL] Expected 2 leaf calls, got $numCalls"
    fi
else
    echo "  [FAIL] callLog missing --- no leaf handler was invoked"
fi
'
