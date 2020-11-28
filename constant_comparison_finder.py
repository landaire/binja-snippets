#
#
def match_comparison_against_const(insn):
	if insn.operation != HighLevelILOperation.HLIL_IF:
		return False
	if insn.condition.operation != HighLevelILOperation.HLIL_CMP_NE and insn.condition.operation != HighLevelILOperation.HLIL_CMP_E:
		return False
	if insn.condition.right.operation != HighLevelILOperation.HLIL_CONST:
		return False
	return True

def match_case_against_const(insn):
	if insn.operation != HighLevelILOperation.HLIL_CASE:
		return False

	for value in insn.values:
		if value.operation == HighLevelILOperation.HLIL_CONST:
			return True

	return False

functions = current_view.functions
found_consts = {}
consts_to_find = [0xE] #[0x2E, 0x2F, 0x2B, 0x13, 0x16, 0x18, 0x20]
while functions:
	function = functions.pop()
	if function is None:
		continue

	for block in function.hlil:
		for insn in block:
			if match_comparison_against_const(insn):
				constant = insn.condition.right.constant
				if constant in consts_to_find:
					if function not in found_consts:
						found_consts[function] = []
					found_consts[function].append((insn.address, constant, 'cmp'))
			elif match_case_against_const(insn):
				for value in insn.values:
					if value.operation == HighLevelILOperation.HLIL_CONST:
						constant = value.constant
						if constant in consts_to_find:
							if function not in found_consts:
								found_consts[function] = []
							found_consts[function].append((insn.address, constant, 'case'))				


sorted_results = []
for function, consts in found_consts.items():
	found_matches_unique = list(set(map(lambda const_data: hex(const_data[1]), consts)))
	num_matches = len(found_matches_unique)
	found_matches_unique.sort()
	sorted_results.append((function, consts, num_matches, found_matches_unique))

sorted_results = sorted(sorted_results, key=lambda res: res[2])

for res in sorted_results:
	function, consts, count, found_matches_unique = res
	joined_matches = ", ".join(found_matches_unique)
	print("{}: {}".format(function.name, joined_matches))
	for const_data in consts:
		address, constant_value, result_type = const_data
		print("    {}: {} ({})".format(hex(address), hex(constant_value), result_type))