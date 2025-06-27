"""ChatGPT website automation using Playwright."""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import logging
from typing import Optional

class ChatGPTInterface:
    def __init__(self, email: str, password: str, project_name: str = "trading bot", headless: bool = True, model: str = "o3"):
        self.email = email
        self.password = password
        self.project_name = project_name
        self.model = model
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        self.open_browser()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def open_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto("https://chat.openai.com")
        self._login()
        self._ensure_project()
        logging.info("ChatGPT ready.")

    def _login(self):
        # Skip if already logged‑in (cookies persisted)
        if "chat.openai.com/chat" in self.page.url:
            return
        try:
            self.page.get_by_label("Email address").fill(self.email)
            self.page.get_by_role("button", name="Continue").click()
            self.page.get_by_label("Password").fill(self.password)
            self.page.get_by_role("button", name="Continue").click()
            self.page.wait_for_url("https://chat.openai.com/chat*", timeout=60000)
        except PlaywrightTimeoutError as e:
            raise RuntimeError("OpenAI login failed. Check credentials or UI selectors.") from e

    def _ensure_project(self):
        try:
            # Open project dropdown (layout may change)
            self.page.get_by_role("button", name="Projects").click(timeout=5000)
            projects = self.page.locator(f"text={self.project_name}")
            if projects.count() == 0:
                self.page.get_by_role("button", name="New project").click()
                self.page.fill("input[placeholder='Name your project']", self.project_name)
                self.page.press("input[placeholder='Name your project']", "Enter")
            else:
                projects.first.click()
        except PlaywrightTimeoutError:
            logging.warning("Project dropdown not found; continuing without projects support.")

    def _ensure_model(self):
        try:
            selector = self.page.get_by_role("button", name=self.model.upper(), exact=True)
            selector.click(timeout=2000)
        except PlaywrightTimeoutError:
            # Open model menu and select
            self.page.get_by_role("button", name="Model").click()
            self.page.get_by_role("option", name=self.model).click()

    def send_prompt(self, prompt: str) -> str:
        self._ensure_model()
        textbox = self.page.get_by_role("textbox")
        textbox.fill(prompt)
        textbox.press("Enter")
        self.page.wait_for_selector(".markdown", timeout=120_000)  # Response container
        messages = self.page.locator(".markdown").all()
        response = messages[-1].inner_text()
        return response

    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
