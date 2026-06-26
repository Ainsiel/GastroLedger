from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from swagger_ui_bundle import swagger_ui_path


def configure_api_docs(application: FastAPI) -> None:
    application.mount(
        "/assets/swagger-ui",
        StaticFiles(directory=swagger_ui_path),
        name="swagger-ui",
    )

    @application.get("/docs", include_in_schema=False)
    async def swagger_ui():
        return get_swagger_ui_html(
            openapi_url=application.openapi_url,
            title=f"{application.title} - Swagger UI",
            swagger_js_url="/assets/swagger-ui/swagger-ui-bundle.js",
            swagger_css_url="/assets/swagger-ui/swagger-ui.css",
            swagger_ui_parameters={
                "displayRequestDuration": True,
                "filter": True,
                "persistAuthorization": False,
                "tryItOutEnabled": True,
            },
        )
