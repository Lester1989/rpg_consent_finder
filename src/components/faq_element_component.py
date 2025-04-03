from nicegui import ui


class FAQElementComponent(ui.expansion):
    question: str
    answer: str

    def __init__(self, question: str, answer: str):
        super().__init__(question.strip("#"), value=True)
        self.question = question
        self.answer = answer
        ui.add_css("""
        .nicegui-markdown h3 {
            font-size: 1.5em;
        }
        .nicegui-markdown h4 {
            font-size: 1.25em;
        }
        """)
        self.content()

    @ui.refreshable
    def content(self):
        with self.classes(
            "w-full border border-gray-200 rounded p-4 text-lg dark:text-stone-200 text-stone-900 dark:bg-zinc-800 bg-zinc-100"
        ):
            ui.markdown(self.answer).classes("text-sm")
