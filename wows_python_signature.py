#
#
import re

renamed_functions = set([])
called_regex = re.compile(r'([^\s]+)[,:] (not|unexpectedly )?called', flags=re.I)
fn_name_log_prefix_regex = re.compile(r'(([^\s]+::)+([^\s]+)):? ', flags=re.I)

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