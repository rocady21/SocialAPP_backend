from datetime import datetime

def getDaysDate(date):
    now = datetime.now()
    now_format = datetime.strptime(datetime.strftime(now, "%Y-%m-%d"), "%Y-%m-%d")
    
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")

    date_days = datetime.strptime(datetime.strftime(date, "%Y-%m-%d"), "%Y-%m-%d")

    segundos_pasados = (now_format - date_days).total_seconds()

    # ahora hacemos las respectivas cuentas paara pasarlo a dias

    date_in_days = round(((segundos_pasados / 60) / 60) / 24)


    
    return date_in_days