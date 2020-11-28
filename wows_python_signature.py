#
#
renamed_functions = set([])

for string in current_view.strings:
	if "raised a python exception which will not be handled" in string.value:
		str_address = string.start
		possible_fn_name = string.value.split(" ")[0]
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