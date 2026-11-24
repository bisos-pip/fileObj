#!/bin/bash
#
# Test 10 of verify.sh --- the generic lifecycle verbs, leaf and branch side.
#
# Scratch tree (leaves are copies of ./leaf.spcs, a fake consumer):
#   branchA/ftoBranchProc.spcs      leafProcessors=['leaf.spcs'], leavesOrdered=['l2','l1']
#   branchA/l1/leaf.spcs  branchA/l2/leaf.spcs
#   branchA/plain/deep/l4/leaf.spcs (below plain directories: walked in-process)
#   branchA/sub/ftoBranchProc.spcs  (its own branch file: walked as a subprocess)
#   branchA/sub/l3/leaf.spcs
#
# Run from py3/tests (verify.sh does): bash lifecycle/lifecycleTest.sh

here=$(cd "$(dirname "$0")" && pwd)
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
export FTO_TEST_CALLS="$scratch/calls"

pass=0; fail=0
check() {   # check <description> <command...>
  local what="$1"; shift
  if "$@"; then echo "  [PASS] $what"; pass=$((pass + 1)); else echo "  [FAIL] $what"; fail=$((fail + 1)); fi
}
calls()     { cat "$FTO_TEST_CALLS" 2>/dev/null; }
resetCalls(){ : > "$FTO_TEST_CALLS"; }

branchSpcs() {   # branchSpcs <dir> [leavesOrdered python list]
  cat > "$1/ftoBranchProc.spcs" <<EOF
#!/usr/bin/env python
from bisos.fileObj import ftoBranch_seed  # noqa: F401  _atExit_
from bisos.fileObj import ftoBranch_seedInfo

ftoBranch_seedInfo.setup(
    leafProcessors=['leaf.spcs'],
    ${2:+leavesOrdered=$2,}
)

def examples_pcs() -> None:
    pass
EOF
  chmod +x "$1/ftoBranchProc.spcs"
}

A="$scratch/branchA"
mkdir -p "$A/l1" "$A/l2" "$A/plain/deep/l4" "$A/sub/l3"
branchSpcs "$A" "['l2', 'l1']"
branchSpcs "$A/sub"
for leaf in "$A/l1" "$A/l2" "$A/plain/deep/l4" "$A/sub/l3"; do
  cp "$here/leaf.spcs" "$leaf/leaf.spcs"; chmod +x "$leaf/leaf.spcs"
done
cd "$A" || exit 1

echo '=== Test 10a: branch-side fto_prepare reaches every leaf, in order; ungated ==='
resetCalls
out=$(./ftoBranchProc.spcs -i fto_prepare 2>&1)
echo "$out" | grep -E '^== |^  ' | sed 's/^/    /'
check "l2 before l1 (leavesOrdered)" bash -c "calls=\$(cat '$FTO_TEST_CALLS'); [[ \$calls == *'l2 prepare'*'l1 prepare'* ]]"
check "l4 below plain directories reached" grep -qx 'l4 prepare' "$FTO_TEST_CALLS"
check "l3 in the sub-branch reached" grep -qx 'l3 prepare' "$FTO_TEST_CALLS"
check "branchA summary counts ran=3" bash -c "echo '$out' | grep -q 'fto_prepare at $A:  ran=3'"
check "sub-branch printed its own summary (ran=1)" bash -c "echo '$out' | grep -q 'fto_prepare at $A/sub:  ran=1'"

echo '=== Test 10b: gated fto_materialize skips every available leaf ==='
resetCalls
out=$(./ftoBranchProc.spcs -i fto_materialize 2>&1)
check "no materialize action ran" bash -c "! grep -q materialize '$FTO_TEST_CALLS'"
check "summary: skipped=3 at branchA" bash -c "echo '$out' | grep -q 'fto_materialize at $A:  ran=0  skipped=3'"
check "status log line" grep -q 'skipped: control=available at fto_materialize' "$A/l1/leaf.status"

echo '=== Test 10c: fto_enable at the branch, then fto_materialize runs ==='
./ftoBranchProc.spcs -i fto_enable >/dev/null 2>&1
check "every leaf enabled" bash -c "for f in '$A'/l1 '$A'/l2 '$A'/plain/deep/l4 '$A'/sub/l3; do [ \"\$(cat \$f/leaf.control)\" = enabled ] || exit 1; done"
resetCalls
./ftoBranchProc.spcs -i fto_materialize >/dev/null 2>&1
check "materialize ran at all four leaves" bash -c "[ \$(grep -c ' materialize\$' '$FTO_TEST_CALLS') -eq 4 ]"

echo '=== Test 10d: an unregistered verb is unsupported, not a failure ==='
out=$(./ftoBranchProc.spcs -i fto_clean 2>&1)
check "logged skipped: unsupported" grep -q 'skipped: unsupported fto_clean' "$A/l2/leaf.status"
check "summary counts it as skipped, failed=0" bash -c "echo '$out' | grep -q 'fto_clean at $A:  ran=0  skipped=3  failed=0'"

echo '=== Test 10e: a failing action is logged failed and counted ==='
out=$(FTO_TEST_FAIL=verify ./ftoBranchProc.spcs -i fto_verify 2>&1)
check "logged failed:" grep -q 'failed: fto_verify: verify failed (test)' "$A/l1/leaf.status"
check "summary failed=3 at branchA" bash -c "echo '$out' | grep -q 'fto_verify at $A:  ran=0  skipped=0  failed=3'"

echo '=== Test 10f: disabled leaves are left completely alone ==='
./ftoBranchProc.spcs -i fto_disable >/dev/null 2>&1
resetCalls
./ftoBranchProc.spcs -i fto_prepare >/dev/null 2>&1
./ftoBranchProc.spcs -i fto_status >/dev/null 2>&1
check "neither prepare nor status ran" bash -c "[ ! -s '$FTO_TEST_CALLS' ]"

echo '=== Test 10g: a CBM-style gate file (no trailing newline) reads back ==='
printf 'enabled' > "$A/l1/leaf.control"
check "fto_control at the leaf says enabled" bash -c "cd '$A/l1' && ./leaf.spcs -i fto_control 2>&1 | grep -q 'control=enabled'"

echo '=== Test 10h: fto_statusLog at the branch shows each leaf log ==='
out=$(./ftoBranchProc.spcs -i fto_statusLog 2>&1)
check "branch walk printed l1's log" bash -c "echo '$out' | grep -q '== l1: '"

echo '=== Test 10i: options the branch does not know are passed on to every leaf ==='
./ftoBranchProc.spcs -i fto_enable >/dev/null 2>&1   # 10f disabled them
export FTO_TEST_ARGV="$scratch/argv"
: > "$FTO_TEST_ARGV"
out=$(./ftoBranchProc.spcs -i fto_prepare --xTest=1 2>&1)
check "the branch announced it" bash -c "echo '$out' | grep -q 'forwarding to leaves: --xTest=1'"
check "every leaf got --xTest=1 (incl. l3 via the sub-branch)" \
  bash -c "[ \$(grep -c -- '--xTest=1' '$FTO_TEST_ARGV') -eq 4 ] && grep -q '^l3 .*--xTest=1' '$FTO_TEST_ARGV'"
: > "$FTO_TEST_ARGV"
./ftoBranchProc.spcs -i fto_forwardToLeaves --cmndName=fto_prepare --xTest=2 >/dev/null 2>&1
check "fto_forwardToLeaves passes it on too (incl. l3)" \
  bash -c "[ \$(grep -c -- '--xTest=2' '$FTO_TEST_ARGV') -eq 4 ] && grep -q '^l3 .*--xTest=2' '$FTO_TEST_ARGV'"
: > "$FTO_TEST_ARGV"; resetCalls
out=$(./ftoBranchProc.spcs -i fto_prepare --xTest 3 2>&1)
check "the space form is refused" bash -c "echo '$out' | grep -q 'cannot pass --xTest on to the leaves'"
check "and nothing ran" bash -c "[ ! -s '$FTO_TEST_CALLS' ]"
: > "$FTO_TEST_ARGV"
./ftoBranchProc.spcs -i fto_prepare >/dev/null 2>&1
check "without extra options, leaves get only -i fto_prepare" bash -c "! grep -q -- '--' '$FTO_TEST_ARGV'"
unset FTO_TEST_ARGV

echo "=== Test 10: $pass passed, $fail failed ==="
[ $fail -eq 0 ]
