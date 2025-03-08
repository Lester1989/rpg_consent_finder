import logging
import random
import string
from typing import Callable, Optional

from nicegui import app, ui


class NiceGuidedTour:
    TOUR_Z_INDEX = 2000

    def __init__(
        self,
        store_user_progress: bool = True,
        storage_key: str = "guided_tour_progress",
        page_suffix: str = "",
    ):
        self.steps: dict[ui.element, str] = {}
        self.make_visible_funcs: dict[ui.element, Optional[Callable]] = {}
        self.elements: dict[int, ui.element] = {}
        self.current_step: Optional[ui.element] = None
        self.store_user_progress = store_user_progress
        self.base_storage_key = storage_key
        self.page_suffix = page_suffix
        self.goto_prev_page = None
        self.goto_next_page = None
        self.current_step_idx = -1
        self.tooltip_container = (
            ui.column()
            .classes(
                f"absolute z-[{NiceGuidedTour.TOUR_Z_INDEX + 1}] bg-slate-700 border border-gray-300 p-4 w-64"
            )
            .mark("GUIDED")
        )
        self.overlay = ui.html().classes(
            f"fixed top-0 left-0 w-full h-full bg-black/50 z-{NiceGuidedTour.TOUR_Z_INDEX - 1} hidden backdrop-blur-sm"
        )

        with self.tooltip_container:
            self.tooltip_content = ui.markdown("")
            self.tooltip_buttons = ui.row().classes("justify-end")

        self.start_element = None
        self.tooltip_container.set_visibility(False)
        app.on_connect(self.hide_tooltip)  # hide tooltip when page reloads

    @property
    def storage_key(self):
        return (
            f"{self.base_storage_key}_{self.page_suffix}"
            if self.page_suffix
            else self.base_storage_key
        )

    def add_prev_page(self, goto_prev_page):
        """Adds a function to go to the previous page."""
        self.goto_prev_page = goto_prev_page

    def add_next_page(self, goto_next_page):
        """Adds a function to go to the next page."""
        self.goto_next_page = goto_next_page

    def add_step(self, element: ui.element, text: str, make_visible_func=None):
        """Adds a step to the guided tour."""
        if not self.start_element:  # first element added is also the start element
            self.start_element = element
            self.current_step_idx = 0
        # logging.debug(f"Adding guided tour step: {text}")
        self.steps[element] = text
        if make_visible_func:
            self.make_visible_funcs[element] = make_visible_func
        self.elements[len(self.elements)] = element

    def show_step(self, element: ui.element):
        """Shows the tooltip for the given element."""
        if element not in self.steps:
            return

        # maybe bring element into view
        if self.make_visible_funcs.get(element):
            self.make_visible_funcs[element]()

        # restore z-index of previous element
        if self.current_step:
            self.current_step.style(
                remove=f"z-index: {NiceGuidedTour.TOUR_Z_INDEX};", add="z-index: auto;"
            )

        # set current element
        self.current_step = element
        self.current_step_idx = [
            idx for idx, elem in self.elements.items() if elem == element
        ][0]

        if self.store_user_progress:
            app.storage.user[self.storage_key] = self.current_step_idx

        # set tooltip content
        self.tooltip_content.content = self.steps[element]
        logging.debug(
            f"Showing guided tour tooltip for {self.storage_key} at step {self.current_step_idx}: {self.steps[element]}"
        )
        # update tooltip buttons
        self.tooltip_buttons.clear()
        with self.tooltip_buttons:
            if self.current_step_idx > 0:
                ui.button("Prev").on_click(self.prev_step)
            elif self.goto_prev_page:
                ui.button("Prev").on_click(self.goto_prev_page)
            if self.current_step_idx < len(self.elements) - 1:
                ui.button("Next").on_click(self.next_step)
                ui.button("X", color="red").on_click(
                    lambda: self.hide_tooltip(is_close_action=True)
                )
            elif self.goto_next_page:
                ui.button("Next").on_click(self.goto_next_page)
                ui.button("X", color="red").on_click(
                    lambda: self.hide_tooltip(is_close_action=True)
                )
            else:
                ui.button("Finish", color="green").on_click(
                    lambda: self.hide_tooltip(is_close_action=True)
                )

        # show tooltip
        self.tooltip_container.set_visibility(True)
        self.overlay.classes(remove="hidden", add="block")

        # elevate the elements z-index
        element.style(
            remove="z-index: auto;", add=f"z-index: {NiceGuidedTour.TOUR_Z_INDEX};"
        )

        # position the tooltip
        self.position_tooltip(element)

    def position_tooltip(self, element: ui.element):
        """Positions the tooltip next to the element."""
        js_code = f"""
        (function() {{
            const tooltip = document.getElementById('c{self.tooltip_container.id}');
            const element = document.getElementById('c{element.id}');
            if (!tooltip || !element) return;

            function position() {{
                const rect = element.getBoundingClientRect();
                let tooltipLeft, tooltipTop;

                // Check if element is nearly as wide as the page
                if (rect.width > window.innerWidth * 0.8) {{ // Adjust 0.8 as needed
                    // Center the tooltip within the element
                    tooltipLeft = rect.left + (rect.width - tooltip.offsetWidth) / 2;
                    tooltipTop = rect.bottom + 10; // Position below the element
                }} else {{
                    // Position tooltip next to the element
                    tooltipLeft = rect.right + 10;
                    tooltipTop = rect.top;

                    // Check if tooltip goes off the right edge
                    if (tooltipLeft + tooltip.offsetWidth > window.innerWidth) {{
                        tooltipLeft = rect.left - tooltip.offsetWidth - 10;
                    }}

                    // Check if tooltip goes off the left edge
                    if (tooltipLeft < 0) {{
                        tooltipLeft = 10;
                    }}

                    // Check for vertical overlap and adjust
                    if (tooltipTop < rect.bottom && tooltipTop + tooltip.offsetHeight > rect.top) {{
                        if (tooltipTop + tooltip.offsetHeight + 10 < window.innerHeight) {{
                            tooltipTop = rect.bottom + 10; // Shift down
                        }} else if (rect.top - tooltip.offsetHeight - 10 > 0) {{
                            tooltipTop = rect.top - tooltip.offsetHeight - 10; // Shift up
                        }}
                    }}
                }}

                tooltip.style.left = tooltipLeft + 'px';
                tooltip.style.top = tooltipTop + 'px';
            }}

            position(); // Initial positioning

            setTimeout(function() {{
                position(); // Delayed second positioning attempt (for when tabs are used with animated transitions)
            }}, 500); // Adjust the delay as needed (milliseconds)

            setTimeout(function() {{
                tooltip.scrollIntoView({{ behavior: 'smooth', block: 'center' }}); 
            }}, 1000); // Scroll the tooltip into view after 1 second
        }})();
        """
        ui.run_javascript(js_code)

    def next_step(self):
        """Moves to the next step in the tour."""
        if self.current_step is None:
            self.show_step(self.start_element)
            return

        if self.current_step_idx + 1 < len(self.elements):
            self.show_step(self.elements[self.current_step_idx + 1])
        else:
            self.hide_tooltip()

    def prev_step(self):
        """Moves to the previous step in the tour."""
        if self.current_step is None:
            self.show_step(self.start_element)
            return

        if self.current_step_idx >= 1:
            self.show_step(self.elements[self.current_step_idx - 1])
        else:
            self.hide_tooltip()

    def start_tour(self, reset_progress: bool = False, reset_all_tours: bool = False):
        """Starts the guided tour."""
        if self.store_user_progress:
            self.current_step_idx = app.storage.user.get(self.storage_key, 0)
            logging.debug(
                f"Loaded guided tour progress {self.current_step_idx} from storage key {self.storage_key}"
            )
        if reset_progress:
            self.current_step_idx = 0
            app.storage.user[self.storage_key] = 0
        if reset_all_tours:
            for key in app.storage.user.keys():
                if isinstance(key, str) and key.startswith(self.base_storage_key):
                    app.storage.user[key] = 0
        logging.debug(
            f"Starting guided tour {self.storage_key} with {len(self.elements)} steps at step {self.current_step_idx}"
        )
        if self.current_step_idx in self.elements:
            self.show_step(self.elements[self.current_step_idx])

    def hide_tooltip(self, _=None, is_close_action: bool = False):
        """Hides the tooltip."""
        if self.current_step:
            self.current_step.style(
                remove=f"z-index: {NiceGuidedTour.TOUR_Z_INDEX};", add="z-index: auto;"
            )
        self.tooltip_container.set_visibility(False)
        self.overlay.classes(remove="block", add="hidden")
        self.current_step = None
        if is_close_action:
            app.storage.user["active_tour"] = ""
            self.current_step_idx = -1
            if self.store_user_progress:
                for key in app.storage.user.keys():
                    if isinstance(key, str) and key.startswith(self.base_storage_key):
                        app.storage.user[key] = -1


if __name__ in {"__main__", "__mp_main__"}:
    # Example usage:

    @ui.page("/")
    def page_home():
        guided_tour = NiceGuidedTour(page_suffix="home")
        link = ui.link("Go to page A", "/a")
        start_button = ui.button("Start").on_click(
            lambda: guided_tour.start_tour(reset_all_tours=True)
        )
        guided_tour.add_step(start_button, "show start button on home page")
        guided_tour.add_step(link, "show link to page A on home page")
        guided_tour.add_next_page(lambda: ui.navigate.to("/a"))
        ui.timer(1, guided_tour.start_tour, once=True)

    @ui.page("/a")
    def page_a():
        guided_tour = NiceGuidedTour(page_suffix="a")
        ui.link("Go to page B", "/b")
        label = ui.label("Page A")
        guided_tour.add_prev_page(lambda: ui.navigate.to("/"))
        guided_tour.add_next_page(lambda: ui.navigate.to("/b"))
        guided_tour.add_step(label, "show label on page A")
        ui.timer(1, guided_tour.start_tour, once=True)

    @ui.page("/b")
    def page_b():
        guided_tour = NiceGuidedTour(page_suffix="b")
        ui.link("Go to page A", "/a")
        start_button = ui.button("Start").on_click(guided_tour.start_tour)
        guided_tour.add_step(start_button, "show start button on page B")
        ui.timer(1, guided_tour.start_tour, once=True)

    ui.run(
        dark=True,
        storage_secret="".join(
            random.choices(string.ascii_letters + string.digits, k=16)
        ),
    )
