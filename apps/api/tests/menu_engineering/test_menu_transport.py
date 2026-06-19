from gastroledger_api.composition import create_application


def test_menu_catalog_is_a_session_scoped_public_api() -> None:
    schema = create_application().openapi()

    assert schema["paths"]["/api/v1/menu/units"]["get"]["responses"]["200"]
    assert schema["paths"]["/api/v1/menu/units"]["post"]["responses"]["201"]
    assert schema["paths"]["/api/v1/menu/conversions"]["post"]["responses"]["201"]
    assert schema["paths"]["/api/v1/menu/ingredients"]["get"]["responses"]["200"]
    assert schema["paths"]["/api/v1/menu/ingredients"]["post"]["responses"]["201"]
    assert schema["paths"]["/api/v1/menu/ingredients/{ingredientId}/archive"]["post"][
        "responses"
    ]["200"]
    assert schema["paths"]["/api/v1/menu/recipes/sub-recipes"]["get"]["responses"]["200"]
    assert schema["paths"]["/api/v1/menu/recipes/sub-recipes"]["post"]["responses"]["201"]
    assert schema["paths"]["/api/v1/menu/recipes/menu-items"]["get"]["responses"]["200"]
    assert schema["paths"]["/api/v1/menu/recipes/menu-items"]["post"]["responses"]["201"]
    assert schema["paths"][
        "/api/v1/menu/recipes/menu-items/{recipeVersionId}/branch-prices"
    ]["post"]["responses"]["201"]

    for schema_name in (
        "UnitRequest",
        "ConversionFactorRequest",
        "IngredientRequest",
        "SubRecipeVersionRequest",
        "MenuItemVersionRequest",
        "BranchMenuPriceRequest",
    ):
        properties = schema["components"]["schemas"][schema_name]["properties"]
        assert "tenantId" not in properties
        assert "actorId" not in properties
