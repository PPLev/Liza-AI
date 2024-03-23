class BasePackage:
    def __init__(self, hook: callable):
        self.hook = hook
        self.data = {}

    async def run_hook(self):
        await self.hook(self)


class TextPackage(BasePackage):
    def __init__(self, input_text, hook):
        super().__init__(hook)
        self.input_text = input_text

    @property
    def text(self):
        if "text" in self.data:
            return self.data["text"]
        return None

    @text.setter
    def text(self, value):
        if isinstance(value, str):
            self.data["text"] = value
        else:
            raise TypeError(f".text must be str, got {type(value)}")
