from datetime import datetime, date

from flask import g, flash, render_template, session, url_for, request, redirect

from application.blueprint import manager as bp
from server_global import db
import service


@bp.route('/data-transfer/')
@bp.route('/data-transfer/<year>/<month>/')
def data_transfer_overview(year=None, month=None):
    dt = datetime.utcnow()
    # determine the year and month to look up
    if year is None or month is None:
        year, month = dt.strftime('%Y:%m').split(':')

    # determine if we can go back and forth a month
    # m<var> is for comparisons
    # (prev_|next_) vars are padded strings for links 
    # l(p|n)_ are the bounds to check against
    lp_year = g.account.join_timestamp.year
    lp_month = g.account.join_timestamp.month
    lp_date = date(lp_year, lp_month, 1)
    ln_year = dt.year
    ln_month = dt.month
    ln_date = date(ln_year, ln_month, 1)

    myear = int(year)
    mmonth = int(month)

    # prev
    if mmonth == 1:
        pmonth = 12
        pyear = myear - 1
    else:
        pmonth = mmonth - 1
        pyear = myear
    pdate = date(pyear, pmonth, 1)
    if pdate >= lp_date:
        prev_link = True
        prev_year = str(pyear)
        prev_month = str(pmonth).zfill(2)
    else:
        prev_link = False
        prev_year = None
        prev_month = None

    # next
    if mmonth == 12:
        nmonth = 1
        nyear = myear + 1
    else:
        nmonth = mmonth + 1
        nyear = myear
    ndate = date(nyear, nmonth, 1)
    # equality means we are looking at the current month
    if ndate <= ln_date:
        next_link = True
        next_year = str(nyear)
        next_month = str(nmonth).zfill(2)
    else:
        next_link = False
        next_year = None
        next_month = None

    # get all the stats and numbers
    xfer_total = g.account.monthly_transfer_total(year, month)
    if xfer_total is None:
        xfer_total = 0
    else:
        xfer_total = '{xfer:,d}'.format(xfer=xfer_total)
    xfer_daily = g.account.monthly_transfer_daily(year, month)
    if g.account.transfer == 0:
        monthly_limit = 'unlimited'
        monthly_unlimited = True
    else:
        monthly_limit = '{total:,d}'.format(total=g.account.transfer)
        monthly_unlimited = False

    # package and render
    title = 'Data transfer stats for {year}/{month}'.\
        format(year=year, month=month)
    ctx = { 'title': title,
            'year': year,
            'month': month,
            'monthly_limit': monthly_limit,
            'monthly_unlimited': monthly_unlimited,
            'prev_link': prev_link,
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_link': next_link,
            'next_month': next_month,
            'next_year': next_year,
            'xfer_daily': xfer_daily,
            'xfer_total': xfer_total, }
    return render_template('manager/data-transfer/home.jade', **ctx)
