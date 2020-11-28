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

MAX_DEPTH = 10
parsed_functions = []
functions = [(current_function, 0)]
found_consts = []
while functions:
	function, depth = functions.pop()
	if function is None:
		continue

	parsed_functions.append(function)

	for block in function.hlil:
		for insn in block:
			if match_comparison_against_const(insn):
				found_consts.append((function.name, insn.address, depth, insn.condition.right.constant))
	
	if depth < MAX_DEPTH:
		for callee in function.callees:
			if callee not in parsed_functions:
				functions.append((callee, depth+1))
for const_data in found_consts:
	func_name, address, depth, constant_value = const_data
	print("{} @ {} ({}): {}".format(func_name, hex(address), depth, hex(constant_value)))