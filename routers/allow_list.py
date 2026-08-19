from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, model_validator
from typing import Self
from supertokens_python.recipe.session.framework.fastapi import verify_session

from helpers.allow_list import (
    get_allowed_emails,
    add_email_to_allow_list,
    is_email_allowed,
    get_allowed_phone_numbers,
    add_phone_number_to_allow_list,
    is_phone_number_allowed
)

router = APIRouter(prefix="/api/allow-list", tags=["Allow List"], dependencies=[Depends(verify_session)])
#TODO: Admin role check after user roles defined
class AllowListPayload(BaseModel):
    phoneNumber: str | None = None
    email: EmailStr | None = None

    @model_validator(mode="after")
    def ensure_exactly_one(self) -> Self:
        if not (bool(self.phoneNumber) ^ bool(self.email)):
            raise ValueError("You must provide exactly one field: either 'phone' or 'email'.")
            
        return self

@router.get("")
async def get_allowed_list_endpoint():
    allowed_emails = await get_allowed_emails()
    allowed_phones = await get_allowed_phone_numbers()
    return {"emails": allowed_emails, "phoneNumbers": allowed_phones}

@router.post("")
async def add_allow_list_entry_endpoint(payload: AllowListPayload):
    if payload.email:
        email = payload.email.strip()
        if await is_email_allowed(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already present in the allowed list."
            )
        
        await add_email_to_allow_list(email)

    elif payload.phoneNumber:
        phone=payload.phoneNumber.strip()
        clean_phone = phone.lstrip("+")
        if not clean_phone.isdigit() or len(clean_phone) < 7:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Provided value must be a valid phone format."
            )
        
        if await is_phone_number_allowed(phone):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number is already present in the allowed list."
            )
        
        await add_phone_number_to_allow_list(phone)

    return {"status": "OK"}
#409