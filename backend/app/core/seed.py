from sqlmodel import Session, select

from app.core.security import hash_password
from app.domain.models import Role, Permission, UserRoleLink, RolePermissionLink, StudyRoom, Seat, SystemParameter, User


def seed_base_data(session: Session) -> None:
    role_codes = {r.code for r in session.exec(select(Role)).all()}
    if "admin" not in role_codes:
        session.add(Role(code="admin", name="管理员"))
    if "student" not in role_codes:
        session.add(Role(code="student", name="学生"))
    session.commit()

    perm_pairs = [
        ("room.manage", "管理教室"),
        ("reservation.view", "查看全部预约"),
        ("rbac.manage", "管理角色权限")
    ]
    existing_perm = {p.code for p in session.exec(select(Permission)).all()}
    for code, name in perm_pairs:
        if code not in existing_perm:
            session.add(Permission(code=code, name=name))
    session.commit()

    admin = session.exec(select(Role).where(Role.code == "admin")).first()
    student = session.exec(select(Role).where(Role.code == "student")).first()
    if admin:
        permission_ids = [p.id for p in session.exec(select(Permission)).all()]
        linked_perm_ids = {
            rp.permission_id for rp in session.exec(select(RolePermissionLink).where(RolePermissionLink.role_id == admin.id)).all()
        }
        for pid in permission_ids:
            if pid not in linked_perm_ids:
                session.add(RolePermissionLink(role_id=admin.id, permission_id=pid))
    session.commit()

    if not session.exec(select(SystemParameter).where(SystemParameter.key == "max_reservation_hours")).first():
        session.add(SystemParameter(key="max_reservation_hours", value="4"))
    if not session.exec(select(SystemParameter).where(SystemParameter.key == "min_credit_score")).first():
        session.add(SystemParameter(key="min_credit_score", value="60"))
    session.commit()

    room_count = len(session.exec(select(StudyRoom)).all())
    if room_count == 0:
        room = StudyRoom(campus="主校区", building="教学楼A", name="A-101")
        session.add(room)
        session.commit()
        session.refresh(room)
        for idx in range(1, 13):
            session.add(Seat(room_id=room.id, seat_code=f"A101-{idx}", has_power=(idx % 3 == 0), by_window=(idx in [1, 6, 7, 12])))
        session.commit()

    # demo admin account
    demo_admin = session.get(User, "admin001")
    if not demo_admin:
        demo_admin = User(
            id="admin001",
            name="系统管理员",
            password_hash=hash_password("Pass1234"),
            email="admin001@example.com",
        )
        session.add(demo_admin)
        session.commit()

    if admin:
        linked = session.get(UserRoleLink, ("admin001", admin.id))
        if not linked:
            session.add(UserRoleLink(user_id="admin001", role_id=admin.id))
            session.commit()

    # demo student role assignment can be added later per register flow
