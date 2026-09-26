import os
from dotenv import load_dotenv

from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import passwordless, session, dashboard, usermetadata
from supertokens_python.recipe.passwordless import ContactEmailOrPhoneConfig


load_dotenv(dotenv_path=".env.dev")
def init_supertokens():
    init(
        app_info=InputAppInfo(
            app_name="Cocktail App",
            api_domain=os.environ.get("API_DOMAIN"),
            website_domain=os.environ.get("WEBSITE_DOMAIN"),
            api_base_path="/auth",
            website_base_path="/auth"
        ),
        framework='fastapi',
        supertokens_config=SupertokensConfig(
            connection_uri=os.environ.get("SUPERTOKENS_CONNECTION_URI"),
            api_key=os.environ.get("SUPERTOKENS_API_KEY")
        ),
        recipe_list=[
            session.init(),
            usermetadata.init(),
            passwordless.init(
                flow_type="USER_INPUT_CODE",
                contact_config=ContactEmailOrPhoneConfig(),
            ),
            dashboard.init(
                admins=["danhoward22@gmail.com"],
            ),
        ],
        mode='asgi'
    )