form_input_text = "form-control bg-secondary bg-opacity-50 border-secondary text-white"
form_select = "form-select bg-secondary bg-opacity-50 border-secondary text-white"


class FormCustom:
    widget_attrs = dict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.widget_attrs:
            try:
                self.fields[field].widget.attrs.update(self.widget_attrs[field])
            except KeyError:
                pass
