entry_light = "form-control"
entry_dark = "form-control bg-secondary bg-opacity-50 border-secondary text-white"

select_light = "form-select"
select_dark = "form-select bg-secondary bg-opacity-50 border-secondary text-white"


class FormCustom:
    dark = dict()
    light = dict()

    def __init__(self, *args, dark_mode=None, **kwargs):
        super().__init__(*args, **kwargs)
        attrs = self.dark if dark_mode else self.light
        for field in attrs:
            try:
                self.fields[field].widget.attrs.update(attrs[field])
            except KeyError:
                pass
