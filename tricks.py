# (list of bound values()
list = query.boundValues()
for k, v in list.items():
    print(k, ": ", v, "\n")

#to use if else in a sigle line; not really coalescence but it works
    tables = tables_columns(table) if not only_field else only_field