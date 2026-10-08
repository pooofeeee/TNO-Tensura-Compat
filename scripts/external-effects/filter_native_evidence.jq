# Exact method selection only; omitted data never proves absence or semantics.
def wanted($entry; $method):
  any($scope[]; .entry == $entry and .method == $method.name and .descriptor == $method.descriptor);
[.witnesses[] as $w | $w.methods[]? as $m | select(wanted($w.entry; $m)) |
 {entry: $w.entry, owner: $w.class_name, superclass: $w.superclass,
  interfaces: $w.interfaces, witness_id: $w.id, mod_key: $w.mod_key,
  jar_sha256: $w.jar_sha256, entry_sha256: $w.entry_sha256,
  class_annotations: ($w.annotations // []), method: $m}] as $selected |
if ($selected|length) != ($scope|length) or ($scope|unique|length) != ($scope|length)
then error("incomplete or duplicate exact selection; expand raw evidence")
else {raw_evidence_file: $source, filter: "EXACT_METHOD_SELECTION",
 scope: $scope, selection_complete: true, instructions_truncated: false,
 omitted_methods: (([.witnesses[].methods[]?]|length) - ($selected|length)),
 omitted_data_proves_absence: false, selected: $selected}
end
