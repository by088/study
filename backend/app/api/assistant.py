"""
智能助手 — 基于关键词匹配与规则引擎的自然语言交互接口。
支持的意图：
  1. 查询可用座位（"有空座吗"、"哪里有座位"）
  2. 条件筛选座位（"靠窗"、"有电源"、"充电"）
  3. 查询我的预约（"我的预约"、"我定了哪里"）
  4. 查询信用分（"信用分"、"积分"）
  5. 帮我预约（"帮我预约"、"帮我订"）
  6. 取消预约（"取消预约"）
"""

import re
from datetime import date, datetime, time, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.domain.models import (
    Reservation,
    ReservationStatus,
    Seat,
    StudyRoom,
    User,
)

router = APIRouter(prefix="/v1/assistant", tags=["assistant"])


# --------------- request / response ---------------

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    intent: str
    data: Optional[list] = None


# --------------- 意图识别 ---------------

INTENT_PATTERNS = [
    # (意图名, 关键词列表)  —— 顺序决定优先级
    ("cancel",       ["取消预约", "取消订座", "取消我的"]),
    ("book",         ["帮我预约", "帮我订", "帮我约", "我要预约", "我要订"]),
    ("my_credit",    ["信用分", "积分", "我的分数", "分数多少"]),
    ("my_booking",   ["我的预约", "我定了", "我订了", "我预约了", "查预约", "查一下我的"]),
    ("search_seat",  ["靠窗", "窗户", "有电源", "充电", "插座", "电源座位"]),
    ("available",    ["空座", "有座", "有没有座", "还有座位", "哪里有座",
                      "可以自习", "有位置", "能学习", "有空位"]),
    ("help",         ["帮助", "你能做什么", "你会什么", "功能", "怎么用"]),
]


def _detect_intent(text: str) -> str:
    for intent, keywords in INTENT_PATTERNS:
        for kw in keywords:
            if kw in text:
                return intent
    return "unknown"


# --------------- 参数提取 ---------------

def _extract_time_hint(text: str):
    """从文本中提取时间线索，返回 (target_date, start_hour)"""
    today = date.today()
    now_hour = datetime.now().hour

    if "明天" in text:
        target_date = today + timedelta(days=1)
        start_hour = 7
    elif "晚上" in text or "晚" in text:
        target_date = today
        start_hour = max(now_hour, 18)
    elif "下午" in text:
        target_date = today
        start_hour = max(now_hour, 13)
    elif "上午" in text or "早上" in text:
        target_date = today
        start_hour = max(now_hour, 7)
    else:
        target_date = today
        start_hour = max(now_hour, 7)

    # 如果提到具体小时数
    m = re.search(r"(\d{1,2})\s*[点时]", text)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            start_hour = h

    return target_date, start_hour


def _extract_seat_filters(text: str):
    by_window = None
    has_power = None
    if "靠窗" in text or "窗户" in text:
        by_window = True
    if "电源" in text or "充电" in text or "插座" in text:
        has_power = True
    return by_window, has_power


# --------------- 处理器 ---------------

def _handle_available(text: str, user: User, session: Session) -> ChatResponse:
    target_date, start_hour = _extract_time_hint(text)
    by_window, has_power = _extract_seat_filters(text)

    rooms = session.exec(
        select(StudyRoom).where(StudyRoom.enabled == True)
    ).all()

    results = []
    for room in rooms:
        close_hour = int(room.closes_at.split(":")[0])
        if start_hour >= close_hour:
            continue

        stmt = select(Seat).where(Seat.room_id == room.id, Seat.enabled == True)
        if by_window is not None:
            stmt = stmt.where(Seat.by_window == by_window)
        if has_power is not None:
            stmt = stmt.where(Seat.has_power == has_power)
        seats = session.exec(stmt).all()

        for seat in seats:
            avail = _seat_available_hours(session, seat, target_date, start_hour, close_hour)
            if avail > 0:
                tags = []
                if seat.by_window:
                    tags.append("靠窗")
                if seat.has_power:
                    tags.append("有电源")
                results.append({
                    "room": f"{room.campus} {room.building} {room.name}",
                    "room_id": room.id,
                    "seat": seat.seat_code,
                    "seat_id": seat.id,
                    "available_hours": avail,
                    "tags": tags,
                })

    if not results:
        time_desc = f"{target_date} {start_hour}:00 起"
        cond_parts = []
        if by_window:
            cond_parts.append("靠窗")
        if has_power:
            cond_parts.append("有电源")
        cond = "（" + "、".join(cond_parts) + "）" if cond_parts else ""
        return ChatResponse(
            reply=f"抱歉，{time_desc}{cond}暂时没有可用座位。",
            intent="available",
        )

    # 最多展示 10 个
    shown = results[:10]
    lines = [f"为你找到 {len(results)} 个可用座位（{target_date} {start_hour}:00 起）：\n"]
    for i, s in enumerate(shown, 1):
        tag_str = " | ".join(s["tags"]) if s["tags"] else "普通"
        lines.append(f"{i}. {s['room']} - 座位{s['seat']}（可用 {s['available_hours']}h，{tag_str}）")
    if len(results) > 10:
        lines.append(f"\n...还有 {len(results) - 10} 个座位，可进一步筛选。")

    return ChatResponse(reply="\n".join(lines), intent="available", data=shown)


def _handle_search_seat(text: str, user: User, session: Session) -> ChatResponse:
    """带条件筛选的座位搜索"""
    return _handle_available(text, user, session)


def _handle_my_booking(text: str, user: User, session: Session) -> ChatResponse:
    target_date, _ = _extract_time_hint(text)

    reservations = session.exec(
        select(Reservation).where(
            Reservation.user_id == user.id,
            Reservation.reserve_date == target_date,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.active]),
        )
    ).all()

    if not reservations:
        return ChatResponse(
            reply=f"你在 {target_date} 没有进行中的预约。",
            intent="my_booking",
        )

    lines = [f"你在 {target_date} 的预约：\n"]
    data = []
    for r in reservations:
        room = session.get(StudyRoom, r.room_id)
        seat = session.get(Seat, r.seat_id)
        room_name = f"{room.campus} {room.building} {room.name}" if room else "未知"
        seat_code = seat.seat_code if seat else "未知"
        status_map = {"pending": "待签到", "active": "已签到"}
        lines.append(
            f"- {room_name} 座位{seat_code}，{r.start_time.strftime('%H:%M')} 起 {r.hours}小时，"
            f"状态：{status_map.get(r.status, r.status)}"
        )
        data.append({
            "reservation_id": r.id,
            "room": room_name,
            "seat": seat_code,
            "start_time": r.start_time.strftime("%H:%M"),
            "hours": r.hours,
            "status": r.status,
        })

    return ChatResponse(reply="\n".join(lines), intent="my_booking", data=data)


def _handle_my_credit(text: str, user: User, session: Session) -> ChatResponse:
    return ChatResponse(
        reply=f"你当前的信用分为 {user.credit_score} 分，违约次数 {user.default_count} 次。\n"
              f"（信用分低于 60 分将无法预约座位）",
        intent="my_credit",
    )


def _handle_cancel(text: str, user: User, session: Session) -> ChatResponse:
    pending = session.exec(
        select(Reservation).where(
            Reservation.user_id == user.id,
            Reservation.status == ReservationStatus.pending,
        ).order_by(Reservation.id.desc())
    ).first()

    if not pending:
        return ChatResponse(reply="你当前没有可取消的预约。", intent="cancel")

    pending.status = ReservationStatus.canceled
    session.add(pending)
    session.commit()

    room = session.get(StudyRoom, pending.room_id)
    seat = session.get(Seat, pending.seat_id)
    room_name = f"{room.name}" if room else "未知"
    seat_code = seat.seat_code if seat else "未知"

    return ChatResponse(
        reply=f"已为你取消预约：{room_name} 座位{seat_code}（{pending.reserve_date} {pending.start_time.strftime('%H:%M')}）",
        intent="cancel",
    )


def _handle_help(text: str, user: User, session: Session) -> ChatResponse:
    return ChatResponse(
        reply="我是自习室智能助手，你可以这样问我：\n\n"
              "1. \"今天晚上还有空座吗\" — 查询可用座位\n"
              "2. \"帮我找靠窗的座位\" — 按条件筛选\n"
              "3. \"帮我找有电源的座位\" — 按条件筛选\n"
              "4. \"我今天定了哪里的座位\" — 查看你的预约\n"
              "5. \"我的信用分多少\" — 查看信用分\n"
              "6. \"取消预约\" — 取消最近一条待签到预约\n"
              "7. \"明天下午有空座吗\" — 指定时间查询",
        intent="help",
    )


def _handle_unknown(text: str, user: User, session: Session) -> ChatResponse:
    return ChatResponse(
        reply="不好意思，我没有理解你的意思。你可以试试：\n"
              "- \"今天晚上还有空座吗\"\n"
              "- \"帮我找靠窗的座位\"\n"
              "- \"我今天定了哪里的座位\"\n"
              "- \"我的信用分多少\"\n"
              "\n输入 \"帮助\" 查看更多功能。",
        intent="unknown",
    )


HANDLERS = {
    "available":   _handle_available,
    "search_seat": _handle_search_seat,
    "my_booking":  _handle_my_booking,
    "my_credit":   _handle_my_credit,
    "cancel":      _handle_cancel,
    "help":        _handle_help,
    "unknown":     _handle_unknown,
}


# --------------- 工具函数 ---------------

def _seat_available_hours(
    session: Session, seat: Seat, target_date: date, start_hour: int, close_hour: int
) -> int:
    """计算某座位在指定时间的可用小时数"""
    max_hours = close_hour - start_hour
    if max_hours <= 0:
        return 0

    start_dt = datetime.combine(target_date, time(start_hour, 0, 0))
    reservations = session.exec(
        select(Reservation).where(
            Reservation.seat_id == seat.id,
            Reservation.reserve_date == target_date,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.active]),
        )
    ).all()

    best = max_hours
    for r in reservations:
        r_start = datetime.combine(target_date, r.start_time)
        r_end = r_start + timedelta(hours=r.hours)
        if r_start <= start_dt < r_end:
            return 0
        if r_start > start_dt:
            gap = int((r_start - start_dt).total_seconds() // 3600)
            best = min(best, gap)
    return max(0, min(4, best))


# --------------- API 端点 ---------------

@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
):
    text = payload.message.strip()
    intent = _detect_intent(text)
    handler = HANDLERS.get(intent, _handle_unknown)
    return handler(text, current, session)
