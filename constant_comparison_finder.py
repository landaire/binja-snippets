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

functions = current_view.functions
found_consts = {}
consts_to_find = [0x2E, 0x2F, 0x2B]
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
					found_consts[function].append((insn.address, constant))
					break
	if len(found_consts) > 0:
		break


for function, consts in found_consts.items():
	found_matches_unique = list(set(map(lambda const_data: hex(const_data[1]), consts)))
	found_matches_unique.sort()
	joined_matches = ", ".join(found_matches_unique)
	print("{}: {}".format(function.name, joined_matches))
	for const_data in consts:
		address, constant_value = const_data
		print("    {}: {}".format(hex(address), hex(constant_value)))