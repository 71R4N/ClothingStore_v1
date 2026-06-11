import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestCatalogAPI:

    @pytest.mark.asyncio
    async def test_get_products_list(
        self, client: AsyncClient, test_product
    ):
        response = await client.get("/api/v1/catalog/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_product_by_slug(
        self, client: AsyncClient, test_product
    ):
        slug = test_product["product"].slug
        response = await client.get(f"/api/v1/catalog/products/{slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == slug
        assert len(data["variants"]) >= 1

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/catalog/products/nonexistent-slug"
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_category_tree(self, client: AsyncClient, test_product):
        response = await client.get("/api/v1/catalog/categories/tree")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.integration
class TestCartAPI:

    @pytest.mark.asyncio
    async def test_add_and_get_cart(
        self, client: AsyncClient, test_product, auth_headers
    ):
        variant_id = test_product["variant"].id
        csrf_resp = await client.get("/api/v1/auth/csrf")
        csrf_token = csrf_resp.cookies.get("csrf_token")
        add_resp = await client.post(
            "/api/v1/cart/items",
            json={"variant_id": variant_id, "quantity": 2},
            headers={**auth_headers, "X-CSRF-Token": csrf_token},
        )
        assert add_resp.status_code == 201
        get_resp = await client.get(
            "/api/v1/cart/", headers=auth_headers
        )
        assert get_resp.status_code == 200
        cart = get_resp.json()
        assert len(cart["items"]) == 1
        assert cart["items"][0]["quantity"] == 2
        assert cart["total"] == pytest.approx(2990.00 * 2)

    @pytest.mark.asyncio
    async def test_add_nonexistent_variant(
        self, client: AsyncClient, auth_headers
    ):
        csrf_resp = await client.get("/api/v1/auth/csrf")
        csrf_token = csrf_resp.cookies.get("csrf_token")
        response = await client.post(
            "/api/v1/cart/items",
            json={"variant_id": 99999, "quantity": 1},
            headers={**auth_headers, "X-CSRF-Token": csrf_token},
        )
        assert response.status_code == 404
