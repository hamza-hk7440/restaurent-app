from fastapi import HTTPException
from fastapi.responses import RedirectResponse
import traceback
from user_management.application.services.verify_email_service import IVerifyEmailService

class VerifyEmailController:
    def __init__(self, verify_email_service: IVerifyEmailService):
        self.verify_email_service = verify_email_service

    async def verify_email(self, token: str):
        try:
            print(f"[debug][verify_email][controller] request token={token}")
            success = await self.verify_email_service.verify_email(token)
            
            if not success:
                print("[debug][verify_email][controller] validation failed: invalid or expired token")
                raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
                
            print("[debug][verify_email][controller] success")
            # Redirect user to your frontend login or success page
            return RedirectResponse(url="http://localhost:3000/login?verified=true", status_code=303)
            
        except HTTPException:
            raise
        except Exception as e:
            print("[debug][verify_email][controller] failed")
            print(traceback.format_exc())
            raise HTTPException(status_code=400, detail=str(e))