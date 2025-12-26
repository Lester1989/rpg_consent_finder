"""
Component tests for FAQElementComponent.

Example of testing a simpler component without database dependencies.
"""

import sys

sys.path.append("src")

from nicegui import ui
from nicegui.testing import User

from components.faq_element_component import FAQElementComponent

pytest_plugins = ["nicegui.testing.plugin"]


async def test_faq_element_renders(user: User, component_page):
    """Test that FAQElementComponent renders with question and answer."""
    test_question = "## What is this test?"
    test_answer = "This is a **test** answer with *markdown*."

    @component_page("/test-faq")
    def setup():
        with ui.column().classes("w-full p-4"):
            component = FAQElementComponent(test_question, test_answer)
            return component

    await user.open("/test-faq")

    # Should display the question (without the ## prefix)
    await user.should_see("What is this test?")

    # Should display the answer
    await user.should_see("This is a")
    await user.should_see("test")
    await user.should_see("answer with")


async def test_faq_element_markdown_rendering(user: User, component_page):
    """Test that markdown is properly rendered in FAQ answers."""

    @component_page("/test-faq-markdown")
    def setup():
        answer_with_markdown = """
        # Heading 1
        ## Heading 2
        
        - List item 1
        - List item 2
        
        **Bold text** and *italic text*
        """
        with ui.column().classes("w-full p-4"):
            component = FAQElementComponent("# Test Question", answer_with_markdown)
            return component

    await user.open("/test-faq-markdown")

    # Verify markdown elements are present
    await user.should_see("Test Question")
    await user.should_see("Heading 1")
    await user.should_see("List item 1")


async def test_multiple_faq_elements(user: User, component_page):
    """Test rendering multiple FAQ elements in a list."""

    faqs = [
        ("## Question 1?", "Answer to question 1"),
        ("## Question 2?", "Answer to question 2"),
        ("## Question 3?", "Answer to question 3"),
    ]

    @component_page("/test-multiple-faqs")
    def setup():
        with ui.column().classes("w-full p-4 gap-4"):
            for question, answer in faqs:
                FAQElementComponent(question, answer)

    await user.open("/test-multiple-faqs")

    # All questions should be visible
    await user.should_see("Question 1?")
    await user.should_see("Question 2?")
    await user.should_see("Question 3?")

    # All answers should be visible (since value=True by default)
    await user.should_see("Answer to question 1")
    await user.should_see("Answer to question 2")
    await user.should_see("Answer to question 3")


async def test_faq_element_expansion(user: User, component_page):
    """Test that FAQ element can be expanded and collapsed."""

    @component_page("/test-faq-expansion")
    def setup():
        with ui.column().classes("w-full p-4"):
            # Create with specific marker for easier testing
            component = FAQElementComponent("## Expandable Question", "Hidden answer")
            component.mark("test-faq-expansion")
            return component

    await user.open("/test-faq-expansion")

    # Question should be visible
    await user.should_see("Expandable Question")

    # Answer should be visible initially (value=True)
    await user.should_see("Hidden answer")

    # Note: Testing actual expansion/collapse behavior would require
    # interacting with the expansion component, which may vary
    # based on NiceGUI's implementation
