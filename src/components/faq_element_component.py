import logging
from nicegui import ui, app


class FAQElementComponent(ui.expansion):
    question: str
    answer: str

    def __init__(self, question: str, answer: str):
        super().__init__(question, value=True)
        self.question = question
        self.answer = answer
        self.content()

    @ui.refreshable
    def content(self):
        with self.classes("w-full border border-gray-200 rounded p-4"):
            ui.markdown(self.answer).classes("text-md")
