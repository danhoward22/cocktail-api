import os
from dotenv import load_dotenv

from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import passwordless, session, dashboard, emailverification, usermetadata
from supertokens_python.recipe.passwordless import ContactEmailOrPhoneConfig, InputOverrideConfig

from helpers.allow_list import override_passwordless_apis

load_dotenv()
def init_supertokens():
    init(
        app_info=InputAppInfo(
            app_name="Block Monster Software",
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
                override=InputOverrideConfig(
                    apis=override_passwordless_apis,
                ),
            ),
            emailverification.init(mode='REQUIRED'),
            dashboard.init(
                admins=["danhoward22@gmail.com"],
            ),
        ],
        mode='asgi' # use wsgi if you are running using gunicorn
    )