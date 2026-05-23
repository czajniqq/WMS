from datetime import datetime

def read_event_log(since: datetime, min_level: str = "WARNING") -> list:
    try:
        import win32evtlog
        import win32evtlogutil
        import win32con
    except ImportError:
        return []

    level_map = {
        "INFORMATION": 4,
        "WARNING": 3,
        "ERROR": 2,
        "CRITICAL": 1,
        "AUDIT_FAILURE": 0,
    }
    min_level_num = level_map.get(min_level.upper(), 3)

    event_type_map = {
        win32con.EVENTLOG_INFORMATION_TYPE: "INFORMATION",
        win32con.EVENTLOG_WARNING_TYPE: "WARNING",
        win32con.EVENTLOG_ERROR_TYPE: "ERROR",
        win32con.EVENTLOG_AUDIT_FAILURE: "AUDIT_FAILURE",
        win32con.EVENTLOG_AUDIT_SUCCESS: "INFORMATION",
    }

    results = []
    for channel in ("System", "Application"):
        try:
            handle = win32evtlog.OpenEventLog(None, channel)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            while True:
                events = win32evtlog.ReadEventLog(handle, flags, 0)
                if not events:
                    break
                
                stop_reading = False
                
                for ev in events:
                    ts = ev.TimeGenerated
                    event_dt = ts if isinstance(ts, datetime) else datetime(*ts[:6])
                    
                    if event_dt < since:
                        stop_reading = True
                        break
                    
                    ev_type = ev.EventType
                    level_str = event_type_map.get(ev_type, "INFORMATION")
                    level_num = level_map.get(level_str, 4)
                    if level_num > min_level_num:
                        continue
                    
                    try:
                        msg = win32evtlogutil.SafeFormatMessage(ev, channel)
                    except Exception:
                        msg = str(ev.StringInserts) if ev.StringInserts else ""
                    msg = (msg or "")[:2000]
                    results.append({
                        "event_time": event_dt.isoformat(),
                        "level": level_str,
                        "source": ev.SourceName,
                        "event_id": ev.EventID & 0xFFFF,
                        "message": msg,
                    })
                
                if stop_reading:
                    break
                    
            win32evtlog.CloseEventLog(handle)
        except Exception:
            continue
    return results
