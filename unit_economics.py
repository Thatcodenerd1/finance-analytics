"""
SaaS Unit Economics Calculator
Computes LTV, CAC, LTV:CAC ratio, Payback Period, and Magic Number.
Relevant to: Ramp, Brex, Stripe, Rippling — unit economics are the foundation of SaaS finance.

Key metrics:
  LTV  = ARPU × Gross Margin % × (1 / Churn Rate)
  CAC  = (Sales + Marketing Spend) / New Customers Acquired
  LTV:CAC  ≥ 3x is healthy; < 1x means you lose money on every customer
  Payback  = CAC / (ARPU × Gross Margin %)
  Magic Number = Net New ARR / Prior Quarter S&M Spend (>0.75 = efficient growth)

Usage:
    python unit_economics.py --arpu 800 --gm 0.72 --churn 0.02 \
        --sm-spend 500000 --new-customers 120 --net-new-arr 1200000
"""
import argparse

def compute_ltv(arpu, gross_margin, monthly_churn):
    if monthly_churn<=0: return float('inf')
    return arpu * gross_margin * (1/monthly_churn)

def compute_cac(sm_spend, new_customers):
    if new_customers==0: return float('inf')
    return sm_spend / new_customers

def compute_payback_months(cac, arpu, gross_margin):
    monthly_gm_revenue=arpu*gross_margin
    if monthly_gm_revenue<=0: return float('inf')
    return cac/monthly_gm_revenue

def compute_magic_number(net_new_arr, prior_sm_spend):
    if prior_sm_spend<=0: return 0
    return net_new_arr/prior_sm_spend

def health_check(ltv_cac, payback, magic):
    issues=[]; status='✅ Healthy'
    if ltv_cac<1: issues.append("🚨 LTV:CAC < 1 — losing money on every customer")
    elif ltv_cac<3: issues.append("⚠️  LTV:CAC < 3 — below benchmark (aim for 3x+)")
    if payback>24: issues.append("🚨 Payback > 24 months — too long, burn risk")
    elif payback>18: issues.append("⚠️  Payback 18-24 months — approaching danger zone")
    if magic<0.5: issues.append("⚠️  Magic Number < 0.5 — low GTM efficiency")
    elif magic>0.75: issues.append("✅ Magic Number > 0.75 — efficient growth engine")
    if issues: status='⚠️  Needs Attention'
    return status, issues

def print_report(arpu,gm,churn,sm,nc,nna,prior_sm):
    ltv=compute_ltv(arpu,gm,churn)
    cac=compute_cac(sm,nc)
    ltv_cac=ltv/cac if cac>0 else 0
    payback=compute_payback_months(cac,arpu,gm)
    magic=compute_magic_number(nna,prior_sm)
    status,issues=health_check(ltv_cac,payback,magic)

    print(f"\n{'UNIT ECONOMICS REPORT':^55}\n{'='*55}")
    print(f"  {'ARPU (monthly)':<30} ${arpu:,.0f}")
    print(f"  {'Gross Margin':<30} {gm*100:.0f}%")
    print(f"  {'Monthly Churn':<30} {churn*100:.1f}%")
    print(f"  {'S&M Spend (quarter)':<30} ${sm:,.0f}")
    print(f"  {'New Customers':<30} {nc}")
    print(f"\n  {'─'*51}")
    print(f"  {'Customer LTV':<30} ${ltv:,.0f}")
    print(f"  {'CAC':<30} ${cac:,.0f}")
    print(f"  {'LTV : CAC':<30} {ltv_cac:.1f}x {'✅' if ltv_cac>=3 else '⚠️'}")
    print(f"  {'Payback Period':<30} {payback:.0f} months {'✅' if payback<=18 else '⚠️'}")
    print(f"  {'Magic Number':<30} {magic:.2f} {'✅' if magic>=0.75 else '⚠️'}")
    print(f"\n  Status: {status}")
    for issue in issues: print(f"  {issue}")
    print("="*55)

if __name__=='__main__':
    p=argparse.ArgumentParser(description='SaaS Unit Economics Calculator')
    p.add_argument('--arpu',type=float,required=True,help='Monthly revenue per user ($)')
    p.add_argument('--gm',type=float,required=True,help='Gross margin (0-1, e.g. 0.72)')
    p.add_argument('--churn',type=float,required=True,help='Monthly churn rate (0-1, e.g. 0.02)')
    p.add_argument('--sm-spend',type=float,required=True,help='Quarterly S&M spend ($)')
    p.add_argument('--new-customers',type=int,required=True,help='New customers acquired this quarter')
    p.add_argument('--net-new-arr',type=float,default=0,help='Net new ARR this quarter ($)')
    p.add_argument('--prior-sm-spend',type=float,default=None,help='Prior quarter S&M spend for Magic Number ($)')
    a=p.parse_args()
    prior=a.prior_sm_spend if a.prior_sm_spend else a.sm_spend
    print_report(a.arpu,a.gm,a.churn,a.sm_spend,a.new_customers,a.net_new_arr,prior)
