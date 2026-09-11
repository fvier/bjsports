"""Billing-cycle credit arithmetic; no database or implicit clock access."""
import re
from calendar import monthrange
from datetime import date, timedelta

MODALITIES = {'Jiu-Jitsu', 'Boxe', 'Muay Thai'}
SCHEDULE_LABELS = {'ter-qui': '2 aulas por semana', 'seg-qua-sex': '3 aulas por semana', 'todos': 'Ilimitado'}


def billing_period(reference, due_day):
    def boundary(year, month):
        return date(year, month, min(due_day, monthrange(year, month)[1]))
    current = boundary(reference.year, reference.month)
    if reference < current:
        previous = current.replace(day=1) - timedelta(days=1)
        return boundary(previous.year, previous.month), current
    following = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
    return current, boundary(following.year, following.month)


def weekly_allowance(plan_text):
    normalized = (plan_text or '').lower()
    # The selected frequency follows the bullet; names can contain legacy days.
    normalized = normalized.split('•', 1)[-1].split('—', 1)[0]
    if 'ilimitado' in normalized or 'todos' in normalized:
        return 0
    if '2 aulas' in normalized or ('ter' in normalized and 'qui' in normalized):
        return 2
    if '3 aulas' in normalized or all(day in normalized for day in ('seg', 'qua', 'sex')):
        return 3
    return None


def released_credits(start, reference, allowance):
    return max(0, ((reference - start).days // 7 + 1) * allowance)


def contract_plan_name(value):
    value = (value or '').split('•')[0].split('—')[0].strip()
    value = re.sub(r'\s*\((?:Seg,\s*Qua,\s*Sex|Ter,\s*Qui)\)\s*$', '', value)
    value = re.sub(r'^[^\w]+', '', value)
    return re.sub(r'^plano\s+', '', value, flags=re.IGNORECASE).strip().casefold()
