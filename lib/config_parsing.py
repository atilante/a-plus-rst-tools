
def parse_date(src, allow_empty=False):
    """Parses a date from natural text into and converts it to standard format.
    
    Parameters:
    src: string containing a date text in one of the formats:
         * 'date'
         * 'date time'
         where:
         * 'date' is either in format 'dd.mm.YYYY' or 'YYYY-mm-dd', where
           'dd' day of month (01..31), 'mm' is number of month (01..12) and
           'YYYY' is the year. For example: '25.09.2020' or '2020-09-25'.
         * 'time' is one of the following:
           'HH'       hour in 24-hour clock
           'HH:MM'    minutes
           'HH:MM:SS' seconds
           fallback: set to 12:00 noon

    allow_empty: if True, allows (src == None)

    Returns:
    Date string in one of the following formats:
    'YYYY-mm-dd HH'
    'YYYY-mm-dd HH:MM'
    'YYYY-mm-dd HH:MM:SS'
    """
    if allow_empty and not src:
        return None

    parts = src.split(u' ', 1)
    d = parts[0] # date
    t = parts[1] if len(parts) > 1 else '' # time

    if re.match(r'^\d\d.\d\d.\d\d\d\d$', d):
        # Date in format DD.MM.YYYY (Date, Month, Year)
        # -> convert to YYYY-MM-DD
        ds = d.split('.')
        d = ds[2] + u'-' + ds[1] + u'-' + ds[0]

    elif re.match(r'^\d\d\d\d-\d\d-\d\d$', d):
        # Date in format YYYY-MM-DD (Year, Month, Date):
        # accepted as it is
        pass
    else:
        raise SphinxError(u'Invalid date ' + d)

    if not re.match(r'^\d\d(:\d\d(:\d\d)?)?$', t):
        t = u'12:00'
    return d + u' ' + t
