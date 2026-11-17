import os
from typing import Any
from dotenv import load_dotenv

from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import passwordless, session, dashboard, usermetadata, userroles
from supertokens_python.recipe.passwordless import ContactEmailOrPhoneConfig

from supertokens_python.asyncio import list_users_by_account_info
from supertokens_python.recipe.passwordless.interfaces import APIInterface, APIOptions
from supertokens_python.recipe.session.interfaces import SessionContainer
from supertokens_python.types import GeneralErrorResponse
from supertokens_python.types.base import AccountInfoInput

load_dotenv(dotenv_path=".env.dev")

def override_passwordless_apis(original_implementation: APIInterface):
    original_create_code_post = original_implementation.create_code_post

    async def create_code_post(
        email: str | None,
        phone_number: str | None,
        session: SessionContainer | None,
        should_try_linking_with_session_user: bool | None,
        tenant_id: str,
        api_options: APIOptions,
        user_context: dict[str, Any],
    ):
        if email is not None:
            existing_user = await list_users_by_account_info(
                tenant_id, AccountInfoInput(email=email)
            )
            user_with_passwordless = next(
                (
                    user
                    for user in existing_user
                    if any(
                        login_method.recipe_id == "passwordless"
                        and login_method.has_same_email_as(email)
                        for login_method in user.login_methods
                    )
                ),
                None,
            )
            if user_with_passwordless is None:
                # sign up attempt
                # TODO: include admin email in response
                return GeneralErrorResponse("Sign ups disabled. Please contact admin.")
        else:
            assert phone_number is not None
            existing_user = await list_users_by_account_info(
                tenant_id, AccountInfoInput(phone_number=phone_number)
            )
            user_with_passwordless = next(
                (
                    user
                    for user in existing_user
                    if any(
                        login_method.recipe_id == "passwordless"
                        and login_method.has_same_phone_number_as(phone_number)
                        for login_method in user.login_methods
                    )
                ),
                None,
            )
            if user_with_passwordless is None:
                # sign up attempt
                # TODO: include admin email in response
                return GeneralErrorResponse("Sign ups disabled. Please contact admin.")

        return await original_create_code_post(
            email,
            phone_number,
            session,
            should_try_linking_with_session_user,
            tenant_id,
            api_options,
            user_context,
        )

    original_implementation.create_code_post = create_code_post
    return original_implementation

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
            userroles.init(),
            usermetadata.init(),
            passwordless.init(
                flow_type="USER_INPUT_CODE",
                contact_config=ContactEmailOrPhoneConfig(),
                override=passwordless.InputOverrideConfig(
                    apis=override_passwordless_apis,
                ),
            ),
            dashboard.init(
                admins=["danhoward22@gmail.com"],
            ),
        ],
        mode='asgi'
    )