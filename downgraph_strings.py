#
#
def match_load_const_ptr(insn):
    # rcx = 0x14170a2c0
    if insn.operation != LowLevelILOperation.LLIL_SET_REG:
        return False

    if insn.src.operation != LowLevelILOperation.LLIL_CONST_PTR:
        return False

    return True

MAX_DEPTH = 10
parsed_functions = []
functions = [(current_function, 0)]
while functions:
	function, depth = functions.pop()
	if function is None:
		continue

	parsed_functions.append(function)

	for block in function.llil:
		for insn in block:
			if match_load_const_ptr(insn):
				string_data = current_view.get_string_at(insn.src.constant)
				if string_data is None:
					continue
				print("{} @ {} ({}): {}".format(function.name, hex(insn.src.constant), depth, string_data))
	
	if depth < MAX_DEPTH:
		for callee in function.callees:
			if callee not in parsed_functions:
				functions.append((callee, depth+1))