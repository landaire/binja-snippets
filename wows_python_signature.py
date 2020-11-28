#
#
import re

def match_call_dispatch_python_devent(insn, dispatch_routine_addr):
    # return maybe_dispatch_python_event("onSetCameraObserveMode", 1, 1, tsc#0, arg3#0) __tailcall
    if insn.operation != HighLevelILOperation.HLIL_TAILCALL:
        return False

    # maybe_dispatch_python_event
    if insn.dest.operation != HighLevelILOperation.HLIL_CONST_PTR:
        return False
	
    if insn.dest.constant != dispatch_routine_addr:
        return False

    if len(insn.params) < 1:
        return False

    # "onSetCameraObserveMode"
    if insn.params[0].operation != HighLevelILOperation.HLIL_CONST_PTR:
        return False
	
    return True

def perform_rename():
	renamed_functions = set([])
	called_regex = re.compile(r'([^\s]+)[,:] (not|unexpectedly )?called', flags=re.I)
	fn_name_log_prefix_regex = re.compile(r'(([^\s]+::)+([^\s]+)):? ', flags=re.I)

	python_function_dispatch_routine = current_view.get_symbols_by_name("maybe_dispatch_python_event")
	if len(python_function_dispatch_routine) == 1:
		python_function_dispatch_routine = current_view.get_function_at(python_function_dispatch_routine[0].address)

	for func_dispatch_caller in python_function_dispatch_routine.callers:
		for block in func_dispatch_caller.hlil:
			for insn in block:
				if match_call_dispatch_python_devent(insn, python_function_dispatch_routine.start):
					string_data = current_view.get_string_at(insn.params[0].constant)
					if string_data is None:
						continue
					new_name = string_data.value
					existing_fn_count = len(current_view.get_symbols_by_name(new_name))
					if existing_fn_count > 0:
						new_name = new_name + "_" + str(existing_fn_count)
					func_dispatch_caller.name = new_name
					renamed_functions.add(func_dispatch_caller)

	for string in current_view.strings:
		possible_fn_name = None
		str_address = string.start
		matched_called_regex = called_regex.match(string.value)
		matched_fn_name_log_prefix = fn_name_log_prefix_regex.match(string.value)
		if "raised a python exception which will not be handled" in string.value:
			possible_fn_name = string.value.split(" ")[0]
		elif matched_fn_name_log_prefix:
			possible_fn_name = matched_fn_name_log_prefix.group(1)
		elif matched_called_regex:
			possible_fn_name = matched_called_regex.group(1)
		else:
			continue
	
		if possible_fn_name is None:
			continue

		existing_fn_count = len(current_view.get_symbols_by_name(possible_fn_name))

		for xref in current_view.get_code_refs(str_address):
			new_name = possible_fn_name
			if existing_fn_count > 0:
				new_name += str(existing_fn_count)

			existing_fn_count += 1
			function = xref.function

			if function in renamed_functions:
				continue

			if function.name.startswith("sub_"):
				xref.function.name = new_name
				renamed_functions.add(function)

	print("Renamed {} functions".format(len(renamed_functions)))

perform_rename()