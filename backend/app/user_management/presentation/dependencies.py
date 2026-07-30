from user_management.application.use_cases.commands.change_email_by_admin_uc import ChangeEmailByAdminUseCase
from user_management.application.use_cases.queries.display_profile_info_uc import DisplayProfileInfoUseCase
from user_management.application.use_cases.commands.login_for_students_uc import LoginForStudentsUseCase
from user_management.presentation.controllers.verify_email_controller import VerifyEmailController
from user_management.presentation.controllers.forget_password_controller import ForgetPasswordController
from user_management.infrastructure.external.verify_email_repository import VerifyEmailRepository
from user_management.infrastructure.external.forget_password_repository import ForgetPasswordRepository
from fastapi import Depends
from user_management.application.use_cases.queries.get_punishments_by_students_id_uc import GetPunishmentsByStudentIdUseCase
from user_management.application.use_cases.commands.edit_student_infos_uc import EditStudentInfosUseCase
from user_management.application.use_cases.commands.unban_student_uc import UnbanStudentUseCase
from user_management.application.use_cases.commands.activate_student_uc import ActivateStudentUseCase
from user_management.application.use_cases.commands.desactivate_student_uc import DesactivateStudentUseCase
from user_management.application.use_cases.commands.ban_student_uc import BanStudentUseCase
from user_management.presentation.controllers.student_controller import StudentController
from supabase import AsyncClient
from user_management.application.use_cases.commands.logout_uc import LogoutUseCase
from user_management.presentation.controllers.logout_controller import LogoutController
from sqlalchemy.ext.asyncio import AsyncSession
from user_management.application.dtos.punishment_dto import PunishmentDTO
from user_management.infrastructure.events.user_event_handler import EmailChangedEventHandler
from user_management.presentation.controllers.verify_email_controller import VerifyEmailController
from user_management.infrastructure.config.database import DatabaseConfig
from user_management.application.use_cases.commands.change_email_by_student_uc import ChangeEmailByStudentUseCase
from user_management.presentation.session import get_supabase_client
from user_management.application.use_cases.commands.create_student_uc import CreateStudentUseCase
from user_management.application.use_cases.commands.forget_password_uc import ForgetPasswordUseCase
from user_management.infrastructure.database.repositories.user_repository import UserRepository
from user_management.presentation.controllers.admin_controller import AdminController
from user_management.application.use_cases.commands.change_password_by_student_uc import ChangePasswordByStudentUseCase
from user_management.infrastructure.external.password_repository import PasswordRepository
from user_management.infrastructure.external.events import EventRepository
from user_management.application.use_cases.commands.login_for_admin_uc import LoginForAdminUseCase
from user_management.infrastructure.external.password_repository import PasswordRepository
from user_management.infrastructure.external.jwt_repository import JWTRepository
from user_management.infrastructure.external.send_mail_repository import SendMailForWlcAndPasswordService
from user_management.infrastructure.external.password_generator_repository import PasswordGeneratorRepository
from user_management.infrastructure.config.database import get_db
from user_management.application.use_cases.commands.change_password_by_admin import ChangePasswordByAdminUseCase
def get_admin_controller(
        db_session: AsyncSession = Depends(get_db),  
) -> AdminController:
    user_repo = UserRepository(db_session=db_session)
    event_repo = EventRepository()
    password_repo = PasswordRepository()
    jwt_repo = JWTRepository(db_session)
    send_mail_repo = SendMailForWlcAndPasswordService()
    password_generator_repo = PasswordGeneratorRepository()
    email_event_handler = EmailChangedEventHandler(send_mail_service=SendMailForWlcAndPasswordService())
    create_student_uc = CreateStudentUseCase(
        student_repo=user_repo,
        event_repo=event_repo,
        password_service=password_repo,
        jwt_service=jwt_repo,
        send_mail_service=send_mail_repo,
        password_generator_service=password_generator_repo
    )
    login_for_admin_uc = LoginForAdminUseCase(
        admin_repo=user_repo,
        jwt_service=jwt_repo,
        password_service=password_repo
    )
    change_password_by_admin_uc = ChangePasswordByAdminUseCase(
        user_repo=user_repo,
        password_service=password_repo,
        events_repo=event_repo,
        password_generator_service=password_generator_repo,
        send_mail_service=send_mail_repo
    )
    change_email_by_admin_uc = ChangeEmailByAdminUseCase(
        user_repo=user_repo,
        events_repo=event_repo,
        jwt_service=jwt_repo,
        email_changed_event_handler=email_event_handler
    )
    ban_student_uc = BanStudentUseCase(
        user_repo=user_repo,
        events_repo=event_repo,
        punishment_dto=PunishmentDTO
    )
    unban_student_uc = UnbanStudentUseCase(
        user_repo=user_repo,
        events_repo=event_repo
    )
    activate_student_uc = ActivateStudentUseCase(
        user_repo=user_repo,
        events_repo=event_repo
    )
    desactivate_student_uc = DesactivateStudentUseCase(
        user_repo=user_repo,
        events_repo=event_repo
    )
    edit_student_infos_uc = EditStudentInfosUseCase(
        user_repo=user_repo,
        events_repo=event_repo
    )
    return AdminController(create_student_uc=create_student_uc, login_for_admin_uc=login_for_admin_uc, change_password_by_admin_uc=change_password_by_admin_uc, change_email_by_admin_uc=change_email_by_admin_uc, ban_student_uc=ban_student_uc, unban_student_uc=unban_student_uc, activate_student_uc=activate_student_uc, desactivate_student_uc=desactivate_student_uc, edit_student_infos_uc=edit_student_infos_uc)
def get_verify_email_controller(
        db_session: AsyncSession = Depends(get_db),
) -> VerifyEmailController:
    student_repo = UserRepository(db_session=db_session)
    jwt_repo = JWTRepository(db_session)
    send_mail_service = SendMailForWlcAndPasswordService()
    password_service = PasswordRepository()
    password_generator_service = PasswordGeneratorRepository()
    service = VerifyEmailRepository(
        user_repo=student_repo,
        send_mail_service=send_mail_service,
        password_service=password_service,
        password_generator_service=password_generator_service,
        jwt_service=jwt_repo
    )
    return VerifyEmailController(verify_email_service=service)

def get_forget_password_controller(
        db_session: AsyncSession = Depends(get_db),
) -> ForgetPasswordController:
    user_repo = UserRepository(db_session=db_session)
    jwt_repo = JWTRepository(db_session)
    send_mail_service = SendMailForWlcAndPasswordService()
    password_service = PasswordRepository()
    event_repo = EventRepository()
    forget_password_service = ForgetPasswordRepository(
        user_repository=user_repo,
        jwt_repository=jwt_repo,
        send_mail_service=send_mail_service
    )
    return ForgetPasswordController(forget_password_uc=forget_password_uc)

def get_student_controller(
        db_session: AsyncSession = Depends(get_db),
) -> StudentController:
    student_repo = UserRepository(db_session=db_session)
    event_repo = EventRepository()
    password_service = PasswordRepository()
    jwt_service = JWTRepository(db_session)
    email_event_handler = EmailChangedEventHandler(send_mail_service=SendMailForWlcAndPasswordService())
    verify_email_controller=get_verify_email_controller(db_session=db_session)
    login_for_students_uc = LoginForStudentsUseCase(
        student_repo=student_repo,
        event_repo=event_repo,
        password_service=password_service,
        jwt_service=jwt_service
    )
    change_password_by_student_uc = ChangePasswordByStudentUseCase(
        user_repo=student_repo,
        password_service=password_service,
        events_repo=event_repo
    )
    change_email_by_student_uc = ChangeEmailByStudentUseCase(
        user_repo=student_repo,
        password_service=password_service,
        events_repo=event_repo,
        jwt_service=jwt_service,
        email_changed_event_handler=email_event_handler
    )
    display_profile_info_uc = DisplayProfileInfoUseCase(
        user_repo=student_repo
    )
    return StudentController(
        login_for_students_uc=login_for_students_uc,
        change_password_by_student_uc=change_password_by_student_uc,
        change_email_by_student_uc=change_email_by_student_uc,
        verify_email_controller=verify_email_controller,
        jwt_service=jwt_service,
        display_profile_info_uc=display_profile_info_uc
        
    )
def get_logout_controller(
        db_session: AsyncSession = Depends(get_db),
) -> LogoutController:
    student_repo = UserRepository(db_session=db_session)
    jwt_service = JWTRepository(db_session)
    logout_uc = LogoutUseCase(
        user_repo=student_repo,
        jwt_service=jwt_service
    )
    return LogoutController(student_repo=student_repo, jwt_service=jwt_service)
def get_get_punishments_by_student_id_controller(
        db_session: AsyncSession = Depends(get_db),
) -> GetPunishmentsByStudentIdUseCase:
    student_repo = UserRepository(db_session=db_session)
    return GetPunishmentsByStudentIdUseCase(user_repo=student_repo)