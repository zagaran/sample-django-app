class ChoicesEnum(object):
    @classmethod
    def values(cls):
        return [value for key, value in vars(cls).items() if not key.startswith("_")]

    @classmethod
    def choices(cls):
        return [(value, value.replace("_", " ").title()) for value in cls.values()]


class ExampleEnum(ChoicesEnum):
    # TODO: delete me; this is just a reference example
    active = "actvie"
    completed = "completed"
