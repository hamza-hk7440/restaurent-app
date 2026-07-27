import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from user_management.infrastructure.config.settings import get_settings
import logging
from user_management.application.services.send_mail_for_wlc_an_password_service import ISendMailForWlcAndPasswordService
import secrets
from datetime import datetime
logger = logging.getLogger(__name__)

class SendMailForWlcAndPasswordService(ISendMailForWlcAndPasswordService):
    def __init__(self):
        self.settings = get_settings()

    async def send_welcome_email(self, receiver_mail: str, password: str) -> None:
        
        subject = f"Welcome to {self.settings.FROM_NAME} - Your Account Created"
        
        html_content = self._get_welcome_email_template(
            student_email=receiver_mail,
            password=password
        )
        
        await self._send_email(
            to_email=receiver_mail,
            subject=subject,
            html_content=html_content
        )
    
    def _get_welcome_email_template(self, student_email: str, password: str) -> str:
        """
        Generate welcome email HTML template
        
        Args:
            student_email: Student email
            password: Temporary password
        
        Returns:
            str: HTML email content
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; margin-top: 20px; border-radius: 5px; }}
                .credentials {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
                .warning {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; color: #856404; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
                .password-box {{ 
                    background-color: #f0f0f0; 
                    padding: 10px; 
                    border-radius: 3px; 
                    font-family: monospace; 
                    font-size: 14px;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {self.settings.FROM_NAME}!</h1>
                </div>
                
                <div class="content">
                    <p>Hello,</p>
                    
                    <p>An administrator has created an account for you on our platform. Your account is now ready to use!</p>
                    
                    <div class="credentials">
                        <h3>Your Login Credentials</h3>
                        <p><strong>Email:</strong> {student_email}</p>
                        <p><strong>Temporary Password:</strong></p>
                        <div class="password-box">{password}</div>
                    </div>
                    
                    <h3>Getting Started</h3>
                    <ol>
                        <li>Go to the {self.settings.FROM_NAME} login page</li>
                        <li>Enter your email: <strong>{student_email}</strong></li>
                        <li>Enter the temporary password above</li>
                        <li><strong>IMPORTANT:</strong> Change your password immediately after first login</li>
                    </ol>
                    
                    <div class="warning">
                        <h3>⚠️ Security Notice</h3>
                        <p>This is a temporary password. For your security, please change it to a new password that only you know after your first login. Never share this password with anyone.</p>
                    </div>
                    
                    <h3>Need Help?</h3>
                    <p>If you have any questions or need assistance, please contact our support team at <strong>{self.settings.REPLY_TO_EMAIL}</strong></p>
                    
                </div>
                
                <div class="footer">
                    <p>&copy; {datetime.now().year} {self.settings.FROM_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    

    
    async def send_password_reset_email(self, receiver_mail: str, password: str) -> None:
        
        subject = f"Reset Your Password - {self.settings.FROM_NAME}"
        
        html_content = self._get_password_reset_email_template(
            receiver_mail=receiver_mail,
            reset_link=password  # 'password' parameter is actually the reset link
        )
        
        await self._send_email(
            to_email=receiver_mail,
            subject=subject,
            html_content=html_content
        )
    
    def _get_password_reset_email_template(self, receiver_mail: str, reset_link: str) -> str:
       
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; margin-top: 20px; border-radius: 5px; }}
                .button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; color: #856404; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
                .link-box {{ background-color: #f9f9f9; padding: 15px; border-radius: 3px; word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset</h1>
                </div>
                
                <div class="content">
                    <p>Hello,</p>
                    
                    <p>You requested a password reset for your {self.settings.FROM_NAME} account associated with <strong>{receiver_mail}</strong>.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    
                    <center>
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </center>
                    
                    <p>Or copy and paste this link in your browser:</p>
                    <div class="link-box">{reset_link}</div>
                    
                    <div class="warning">
                        <h3>⏰ This Link Expires In {self.settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES} Minutes</h3>
                        <p>For security reasons, this password reset link will expire in {self.settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES} minutes. If the link expires, you can request a new one.</p>
                    </div>
                    
                    <h3>Didn't Request This?</h3>
                    <p>If you didn't request a password reset, you can safely ignore this email. Your password will not change unless you click the link above.</p>
                    
                    <p>If you have any concerns about your account security, please contact us at <strong>{self.settings.REPLY_TO_EMAIL}</strong></p>
                    
                </div>
                
                <div class="footer">
                    <p>&copy; {datetime.now().year} {self.settings.FROM_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
   
    async def send_verification_email(self, receiver_mail: str) -> str:
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Create verification link using the configured frontend URL.
        verification_link = f"http://127.0.0.1:8000/auth/verify-email?token={verification_token}"
        
        subject = f"Verify Your Email - {self.settings.FROM_NAME}"
        
        html_content = self._get_verification_email_template(
            receiver_mail=receiver_mail,
            verification_link=verification_link
        )
        
        await self._send_email(
            to_email=receiver_mail,
            subject=subject,
            html_content=html_content
        )
        
        # Return token so it can be saved to database
        return verification_token
    
    def _get_verification_email_template(self, receiver_mail: str, verification_link: str) -> str:
      
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF9800; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; border: 1px solid #ddd; margin-top: 20px; border-radius: 5px; }}
                .button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .info {{ background-color: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; color: #1565c0; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
                .link-box {{ background-color: #f9f9f9; padding: 15px; border-radius: 3px; word-break: break-all; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Verify Your Email Address</h1>
                </div>
                
                <div class="content">
                    <p>Hello,</p>
                    
                    <p>Thank you for registering with {self.settings.FROM_NAME}. To complete your account setup and start using our services, please verify your email address.</p>
                    
                    <p>Click the button below to verify your email:</p>
                    
                    <center>
                        <a href="{verification_link}" class="button">Verify Email</a>
                    </center>
                    
                    <p>Or copy and paste this link in your browser:</p>
                    <div class="link-box">{verification_link}</div>
                    
                    <div class="info">
                        <h3>⏰ Verification Link Expires In {self.settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} Hours</h3>
                        <p>Please verify your email within {self.settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} hours. After that, you'll need to request a new verification link.</p>
                    </div>
                    
                    <h3>Why Verify?</h3>
                    <p>Email verification helps us:</p>
                    <ul>
                        <li>Confirm you own this email address</li>
                        <li>Send you important account notifications</li>
                        <li>Help you recover your account if needed</li>
                    </ul>
                    
                    <p>If you didn't create this account, please ignore this email.</p>
                    
                </div>
                
                <div class="footer">
                    <p>&copy; {datetime.now().year} {self.settings.FROM_NAME}. All rights reserved.</p>
                    <p>Need help? Contact us at {self.settings.REPLY_TO_EMAIL}</p>
                </div>
            </div>
        </body>
        </html>
        """
    

    async def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        try:
            print(f"[debug][mail] preparing email to={to_email} subject={subject}")
            print(f"[debug][mail] EMAIL_LOG_TO_CONSOLE={self.settings.EMAIL_LOG_TO_CONSOLE}")
            # Console logging mode is the safe default for local development.
            if self.settings.EMAIL_LOG_TO_CONSOLE:
                print("[debug][mail] using console mode")
                self._log_email_to_console(to_email, subject, html_content)
                return True
            
            # send via Mailtrap (production)
            print("[debug][mail] using smtp mode")
            return await self._send_via_mailtrap(to_email, subject, html_content)
        
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _log_email_to_console(self, to_email: str, subject: str, html_content: str) -> None:
        
        print("\n" + "=" * 80)
        print("📧 EMAIL LOG (Console Mode - Development)")
        print("=" * 80)
        print(f"To: {to_email}")
        print(f"From: {self.settings.FROM_NAME} <{self.settings.FROM_EMAIL}>")
        print(f"Subject: {subject}")
        print("-" * 80)
        print(html_content)
        print("=" * 80 + "\n")
        
        logger.info(f"Email logged to console: {subject} → {to_email}")
    
    async def _send_via_mailtrap(self, to_email: str, subject: str, html_content: str) -> bool:
        
        try:
            print(f"[debug][mail] smtp host={self.settings.MAILTRAP_HOST} port={self.settings.MAILTRAP_PORT}")
            #create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.settings.FROM_NAME} <{self.settings.FROM_EMAIL}>"
            message["To"] = to_email
            message["Reply-To"] = self.settings.REPLY_TO_EMAIL
            
            #attach HTML content
            message.attach(MIMEText(html_content, "html"))
            
            # Send via Mailtrap SMTP when console mode is disabled.
            with smtplib.SMTP(self.settings.MAILTRAP_HOST, self.settings.MAILTRAP_PORT) as server:
                print("[debug][mail] smtp connection opened")
                server.starttls()
                print("[debug][mail] smtp tls started")
                server.login(self.settings.MAILTRAP_USERNAME, self.settings.MAILTRAP_PASSWORD)
                print("[debug][mail] smtp login ok")
                server.sendmail(
                    self.settings.FROM_EMAIL,
                    to_email,
                    message.as_string()
                )
                print("[debug][mail] smtp sendmail ok")
            
            logger.info(f"Email sent successfully: {subject} → {to_email}")
            return True
        
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
