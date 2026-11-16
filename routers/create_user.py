from fastapi import APIRouter, Depends
from supertokens_python.recipe.passwordless.asyncio import create_magic_link, signinup
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.userroles import UserRoleClaim

from models.create_user import CreateUserResponse

router = APIRouter()

@router.post('/create-user', response_model=CreateUserResponse)
async def create_user(
    email: str,
    session: SessionContainer = Depends(verify_session(
    override_global_claim_validators=lambda global_validators, session, user_context: global_validators +
    [UserRoleClaim.validators.includes("admin")]
))):
    # this will create the user in supertokens if they don't already exist
    await signinup("public", email, None)

    invite_link = await create_magic_link("public", email, None)

    print(invite_link)

    if invite_link:
        return CreateUserResponse(success=False)
    else:
        return CreateUserResponse(success=True, link=invite_link)
    
    # TODO: send invite_link to email
    # TODO: send 200 responspe to client