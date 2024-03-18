class Context:
    def __init__(self, context: dict):
        if context:
            self.context = context
        else:
            self.context = dict()

    def add_context(self, key, context):
        if not self.context[key]:
            self.context[key] = context

    def contextualize(self, key, information):
        """
        Retrieve the contextualized version of information associated with a given key.

        Parameters:
        key (str): The key associated with the context.
        information (str): The information to contextualize.

        Returns:
        str: The contextualized version of the information.
        """
        if key in self.context:
            return f"{information} ({self.context[key]})"
        else:
            return f"No context found for '{key}'"

    def __getattr__(self, key):
        return self.context[key]

    def __setattr__(self, key, value):
        self.context[key] = value

    def __getitem__(self, key):
        return self.context[key]

    def __setitem__(self, key, value):
        self.context[key] = value
