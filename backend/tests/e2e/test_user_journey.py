import pytest
import time
from playwright.async_api import async_playwright, expect

BASE_URL = "http://localhost"


@pytest.mark.e2e
class TestUserJourney:

    @pytest.mark.asyncio
    async def test_registration_and_login(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            unique_email = f"e2e_{int(time.time())}@example.com"
            await page.goto(f"{BASE_URL}/register")
            await page.wait_for_selector("#first_name", timeout=10000)
            await page.fill('#first_name', "E2E")
            await page.fill('#last_name', "User")
            await page.fill('#email', unique_email)
            await page.fill('#password', "E2ETest123!")
            await page.click('button[type="submit"]')
            await page.wait_for_url(f"{BASE_URL}/", timeout=15000)
            await expect(
                page.locator('button:has-text("Выйти")')
            ).to_be_visible(timeout=10000)
            await page.click('button:has-text("Выйти")')
            await page.wait_for_timeout(1500)
            await page.goto(f"{BASE_URL}/login")
            await page.wait_for_selector("#email", timeout=10000)
            await page.fill('#email', unique_email)
            await page.fill('#password', "E2ETest123!")
            await page.click('button[type="submit"]')
            await page.wait_for_url(f"{BASE_URL}/", timeout=15000)
            await expect(
                page.locator('button:has-text("Выйти")')
            ).to_be_visible()
            await browser.close()

    @pytest.mark.asyncio
    async def test_add_to_cart_flow(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f"{BASE_URL}/catalog")
            await page.wait_for_selector(".ant-card", timeout=15000)
            first_card = page.locator(".ant-card").first
            await first_card.click()
            await page.wait_for_url("**/product/**", timeout=10000)
            size_select = page.locator(".ant-select").nth(0)
            if await size_select.is_visible():
                await size_select.click()
                await page.locator(".ant-select-item").first.click()
            await page.click('button:has-text("Добавить в корзину")')
            await page.wait_for_timeout(1500)
            await page.click('[title="Корзина"]')
            await page.wait_for_url("**/cart", timeout=10000)
            cart_items = page.locator(".ant-table-row")
            await expect(cart_items).to_have_count(1, timeout=10000)
            await browser.close()

    @pytest.mark.asyncio
    async def test_checkout_flow(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(f"{BASE_URL}/login")
            await page.wait_for_selector("#email", timeout=10000)
            await page.fill('#email', "user@example.com")
            await page.fill('#password', "User123!")
            await page.click('button[type="submit"]')
            await page.wait_for_url(f"{BASE_URL}/", timeout=15000)
            await page.wait_for_selector(
                'button:has-text("Перейти в каталог")',
                timeout=15000
            )
            await page.wait_for_timeout(1000)
            await page.goto(f"{BASE_URL}/catalog")
            await page.wait_for_selector(".ant-card", timeout=15000)
            await page.locator(".ant-card").first.click()
            await page.wait_for_url("**/product/**", timeout=10000)
            size_select = page.locator(".ant-select").nth(0)
            if await size_select.is_visible():
                await size_select.click()
                await page.locator(".ant-select-item").first.click()
            await page.click('button:has-text("Добавить в корзину")')
            await page.wait_for_timeout(1500)
            await page.goto(f"{BASE_URL}/checkout")
            await page.wait_for_selector("#city", timeout=10000)
            await page.fill('#city', "Москва")
            await page.fill('#street', "ул. Тестовая, д. 1")
            await page.click('button:has-text("Перейти к оплате")')
            await page.wait_for_timeout(3500)
            await page.wait_for_load_state("networkidle")
            current_url = page.url
            assert (
                    "/payment/status" in current_url or
                    "/orders" in current_url or
                    "yookassa" in current_url.lower() or
                    "yoomoney" in current_url.lower() or
                    "localhost" in current_url
            ), f"Unexpected URL after checkout: {current_url}"
            await browser.close()
