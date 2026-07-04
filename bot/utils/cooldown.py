from datetime import datetime, timedelta

def check_cooldown(last_task_str):
    """Возвращает (bool: можно_ли_выполнять, str: сколько_осталось)."""
    if not last_task_str:
        return True, "Доступно сейчас"
    
    last_task = datetime.strptime(last_task_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    diff = now - last_task
    cooldown = timedelta(hours=24)
    
    if diff >= cooldown:
        return True, "Доступно сейчас"
    else:
        remaining = cooldown - diff
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return False, f"{hours} ч {minutes} мин"