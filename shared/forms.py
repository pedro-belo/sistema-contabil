entry_light = "form-control"
entry_dark = "form-control bg-secondary bg-opacity-50 border-secondary text-white"

select_light = "form-select"
select_dark = "form-select bg-secondary bg-opacity-50 border-secondary text-white"


class FormCustom:
    widget_attrs = dict()

    dark = dict()
    light = dict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.widget_attrs:
            try:
                self.fields[field].widget.attrs.update(self.widget_attrs[field])
            except KeyError:
                pass
