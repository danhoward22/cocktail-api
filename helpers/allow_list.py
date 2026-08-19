from typing import Any

from supertokens_python.asyncio import list_users_by_account_info
from supertokens_python.recipe.passwordless.interfaces import (
    APIInterface,
    APIOptions,
)
from supertokens_python.recipe.session.interfaces import SessionContainer
from supertokens_python.recipe.usermetadata.asyncio import (
    get_user_metadata,
    update_user_metadata,
)
from supertokens_python.types import GeneralErrorResponse
from supertokens_python.types.base import AccountInfoInput

#TODO: add user DB table, or reject values that match metadata keys
async def get_allowed_emails():
    metadataResult = await get_user_metadata("emailAllowList")
    allow_list: list[str] = metadataResult.metadata["allowList"] if "allowList" in metadataResult.metadata else []
    return allow_list

async def add_email_to_allow_list(email: str):
    allow_list = await get_allowed_emails()
    allow_list.append(email)
    await update_user_metadata("emailAllowList", {
        "allowList": allow_list
    })

async def is_email_allowed(email: str):
    allow_list = await get_allowed_emails()
    return email in allow_list

async def get_allowed_phone_numbers():
    metadataResult = await get_user_metadata("phoneNumberAllowList")
    allow_list: list[str] = metadataResult.metadata["allowList"] if "allowList" in metadataResult.metadata else []
    return allow_list

async def add_phone_number_to_allow_list(phone_number: str):
    allow_list = await get_allowed_phone_numbers()
    allow_list.append(phone_number)
    await update_user_metadata("phoneNumberAllowList", {
        "allowList": allow_list
    })

async def is_phone_number_allowed(phone_number: str):
    allow_list = await get_allowed_phone_numbers()
    return phone_number in allow_list

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
                if not (await is_email_allowed(email)):
                    return GeneralErrorResponse(
                        "Sign ups disabled. Please contact admin."
                    )
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
                if not (await is_phone_number_allowed(phone_number)):
                    return GeneralErrorResponse(
                        "Sign ups disabled. Please contact admin."
                    )

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
