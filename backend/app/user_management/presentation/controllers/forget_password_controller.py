from fastapi import HTTPException
import traceback

from user_management.application.use_cases.commands.forget_password_uc import ForgetPasswordUseCase


class ForgetPasswordController:
    def __init__(self, forget_password_uc: ForgetPasswordUseCase):
        self.forget_password_uc = forget_password_uc

    async def request_reset(self, email: str):
        try:
            print(f"[debug][forget_password][controller] request email={email!r}")
            result = await self.forget_password_uc.request_reset(email)
            print("[debug][forget_password][controller] success")
            return result
        except Exception as e:
            print("[debug][forget_password][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))

    async def reset_password(self, token: str, new_password: str):
        try:
            print("[debug][reset_password][controller] request token received")
            result = await self.forget_password_uc.reset_password(token, new_password)
            print("[debug][reset_password][controller] success")
            return result
        except Exception as e:
            print("[debug][reset_password][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))
