from fastapi import APIRouter, Depends
from supertokens_python.recipe.passwordless.asyncio import create_magic_link, signinup
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.userroles import UserRoleClaim
from supertokens_python.recipe.userroles.syncio import add_role_to_user
from supertokens_python.recipe.userroles.interfaces import UnknownRoleError

from models.users import UserResponse

router = APIRouter()

@router.post('/create-user', response_model=UserResponse)
async def create_user(
    email: str,
    session: SessionContainer = Depends(verify_session(
        override_global_claim_validators=lambda global_validators, session, user_context: global_validators +
        [UserRoleClaim.validators.includes("admin")]
    ))
):
    # this will create the user in supertokens if they don't already exist
    await signinup("public", email, None)

    invite_link = await create_magic_link("public", email, None)

    print(invite_link)

    if not invite_link:
        return UserResponse(success=False)
    else:
        return UserResponse(success=True, link=invite_link)
    
    # TODO: send invite_link to email
    # TODO: send 200 responspe to client

@router.post("/user-role", response_model=UserResponse)
async def assign_role_to_user(
    user_id: str,
    role: str,
    session: SessionContainer = Depends(verify_session(
        override_global_claim_validators=lambda global_validators, session, user_context: global_validators +
        [UserRoleClaim.validators.includes("admin")]
    ))
):
    res = add_role_to_user("public", user_id, role)
    if isinstance(res, UnknownRoleError):
        return UserResponse(success=False, message="No such role exists")

    if res.did_user_already_have_role:
        return UserResponse(success=True, message="User already has the role")
    
    return UserResponse(success=True)