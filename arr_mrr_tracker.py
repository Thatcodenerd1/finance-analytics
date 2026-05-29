"""
ARR / MRR Movement Tracker
Breaks revenue change into: New, Expansion, Contraction, Churn, Reactivation.
Relevant to: Ramp, Brex, Rippling — every SaaS finance team tracks this waterfall monthly.

This is the revenue waterfall (MRR movement report):
  Ending MRR = Starting MRR + New + Expansion - Contraction - Churn + Reactivation

Usage:
    python arr_mrr_tracker.py --input subscriptions.csv --month 2026-04
"""
import pandas as pd, argparse
from datetime import datetime

def compute_mrr_movements(df, month_str):
    """
    df columns: customer_id, mrr, month (YYYY-MM), status
    status: new | active | expanded | contracted | churned | reactivated
    """
    df=df.copy(); df['month']=df['month'].astype(str)
    current=df[df.month==month_str].copy()
    prev_month=pd.Period(month_str,'M')-1; prev_str=str(prev_month)
    prior=df[df.month==prev_str].copy()

    movements={'New MRR':0,'Expansion MRR':0,'Contraction MRR':0,'Churn MRR':0,'Reactivation MRR':0}
    prior_mrr=prior.set_index('customer_id')['mrr'].to_dict()
    current_mrr=current.set_index('customer_id')['mrr'].to_dict()
    prior_customers=set(prior_mrr); current_customers=set(current_mrr)

    for cid in current_customers-prior_customers: movements['New MRR']+=current_mrr[cid]
    for cid in prior_customers-current_customers: movements['Churn MRR']+=prior_mrr[cid]
    for cid in current_customers&prior_customers:
        diff=current_mrr[cid]-prior_mrr[cid]
        if diff>0: movements['Expansion MRR']+=diff
        elif diff<0: movements['Contraction MRR']+=abs(diff)

    starting=sum(prior_mrr.values()); ending=sum(current_mrr.values())
    net_change=ending-starting

    print(f"\n{'MRR MOVEMENT REPORT — '+month_str:^55}\n{'='*55}")
    print(f"  Starting MRR:        ${starting:>12,.0f}")
    for label,val in movements.items():
        sign='+' if 'Churn' not in label and 'Contraction' not in label else '-'
        print(f"  {label:<22} {sign}${val:>11,.0f}")
    print(f"  {'─'*51}")
    print(f"  Ending MRR:          ${ending:>12,.0f}")
    print(f"  Net Change:          {'+'if net_change>=0 else ''}${net_change:>11,.0f}  ({'+' if net_change>=0 else ''}{net_change/starting*100:.1f}%)")
    print(f"\n  Customers: {len(prior_customers)} → {len(current_customers)}  (Net: {len(current_customers)-len(prior_customers):+d})")
    churn_rate=movements['Churn MRR']/starting*100 if starting>0 else 0
    expansion_rate=movements['Expansion MRR']/starting*100 if starting>0 else 0
    print(f"  MRR Churn Rate:      {churn_rate:.2f}%")
    print(f"  Expansion Rate:      {expansion_rate:.2f}%")
    print(f"  Net Revenue Retention: {(ending-movements['New MRR'])/starting*100:.1f}%")
    print("="*55)
    return movements, starting, ending

if __name__=='__main__':
    p=argparse.ArgumentParser(description='ARR/MRR Movement Tracker')
    p.add_argument('--input',required=True,help='CSV: customer_id, mrr, month (YYYY-MM)')
    p.add_argument('--month',required=True,help='Month to analyze (YYYY-MM)')
    a=p.parse_args()
    df=pd.read_csv(a.input)
    compute_mrr_movements(df,a.month)
