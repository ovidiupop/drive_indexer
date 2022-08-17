# (list of bound values()
list = query.boundValues()
for k, v in list.items():
    print(k, ": ", v, "\n")

#to use if else in a sigle line; not really coalescence but it works
    tables = tables_columns(table) if not only_field else only_field
    variable = desired_value if (or not) condition else default_value
    or for actions
    box.setChecked(True) if is_checked else box.setChecked(False)


# get real name of an object's class
parent_name = self.parent().metaObject().className()

#how to set parent
#to call methods from parent
class Exmpler(QtWidgets.QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(Exmpler, self).__init__(parent=parent, *args, **kwargs)
        # the you can call
        self.parent().parentMethod()

in parent do:
    exampler = Exampler(self)
