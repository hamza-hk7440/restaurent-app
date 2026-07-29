from user_management.domain.events.user_events import EmailChangedEvent
from user_management.application.services.send_mail_for_wlc_an_password_service import ISendMailForWlcAndPasswordService

class EmailChangedEventHandler:
    def __init__(self, send_mail_service: ISendMailForWlcAndPasswordService):
        self.send_mail_service = send_mail_service

    async def handle(self, event: EmailChangedEvent):
        print(f"[debug][EmailChangedEventHandler] Handling EmailChangedEvent for user_id={event.user_id}, new_email={event.new_email}")

        await self.send_mail_service.send_verification_email_for_change(event.new_email, event.verification_token)