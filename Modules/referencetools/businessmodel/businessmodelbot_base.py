"""
Title: Business Model Bot
Version: 1.0
Date Started: Oct 22, 2019
Date Updated: Oct 22, 2019
Author: David Hyongsik Choi
Legal:  All rights reserved.  This code may not be used, distributed, or copied
    without the express written consent of David Hyongsik Choi.
Purpose: Model several different possible business models at once and return results.
Information:  For a client to switch over,  you.client_actualgain >= comp.client_actualgain * (1 + switch_factor)

DEFINITIONS:
edge_rate is growth rate above the comp_fund_perf s.t. you.client_actualgain >= comp.client_actualgain * (1 + switch_factor).
It's how much better your fund's growth rate must be than the competitor's for the client to switch to your fund, given a switch_factor.
A switch_factor is the proportion of the client's take home earnings (earnings after fees are paid) with the competitor that your fund needs to make for the client for them to switch to your fund:
Client switches to your fund if client's take home earnings (your fund) > client's take home earnings (competitor fund) * (1+switchfactor).
IMPORTANT: BECAUSE THE EDGE_RATE IS BY DEFINITION A PROPORTION ABOVE THE COMP RATE, IT IS NON-NEGATIVE.  SO THE FORMULA PRODUCES AN ABSOLUTE VALUE.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.optimize import root
from Modules.numbers import formalnumber, formalnumber_integer


# PERFORMANCE FEE - the rate you'd multiply by the amount client's fund grew to get amount fund gets paid based off performance
# v1 performance fee regime -- fund pays client back amount market beats fund or if losing
def perf_fee_calc(fund_perf, mkt_perf, perf_cut):
    if fund_perf >= mkt_perf:
        if fund_perf < 0:
            return fund_perf  # fund pays client any losses
        else:
            return (fund_perf - mkt_perf) * perf_cut
    else:
        return fund_perf - mkt_perf  # fund pays client amount its losing against market rate


# PERF FEE IF FUND BEATS MARKET REGARDLESS WHETHER FUNDRATE > OR < 0
def perf_fee_calcv2(fund_perf, mkt_perf, perf_cut):
    if fund_perf > mkt_perf:
        return (fund_perf - mkt_perf) * perf_cut
    else:
        return 0


# PERFORMANCE FEE ONLY IF FUND BEATS MARKET AND FUND GROWS
def perf_fee_calcv3(fund_perf, mkt_perf, perf_cut):
    if fund_perf > 0 and fund_perf > mkt_perf:
        return (fund_perf - mkt_perf) * perf_cut
    else:
        return 0


def perf_fee_selector(fund_perf, mkt_perf, perf_cut, perf_fee_regime):
    if perf_fee_regime == 'v1':
        perfee_rate = perf_fee_calc(fund_perf, mkt_perf, perf_cut)
    elif perf_fee_regime == 'v2':
        perfee_rate = perf_fee_calcv2(fund_perf, mkt_perf, perf_cut)
    elif perf_fee_regime == 'v3':
        perfee_rate = perf_fee_calcv3(fund_perf, mkt_perf, perf_cut)
    return perfee_rate


# establishes properties of a fund given inputs
class FundProfile():
    def __init__(
        self,
        profile,
        client_principal,
        num_clients,
        perf_cut,
        aum_rate,
        mkt_perf,
        fund_perf,
        overhead_cost,
        perf_fee_regime
    ):
        self.profile = profile
        self.client_principal = client_principal
        self.num_clients = num_clients
        self.perf_cut = perf_cut
        self.aum_rate = aum_rate
        self.mkt_perf = mkt_perf
        self.fund_perf = fund_perf
        self.overhead_cost = overhead_cost
        self.perf_fee_regime = perf_fee_regime
        # CLIENT GROSS
        self.client_grossgain = self.client_principal * self.fund_perf
        self.client_grossvalue = self.client_principal + self.client_grossgain
        # CLIENT COSTS
        if self.perf_fee_regime == 'v1':
            self.perfee_rate = perf_fee_calc(self.fund_perf, self.mkt_perf, self.perf_cut)
        elif self.perf_fee_regime == 'v2':
            self.perfee_rate = perf_fee_calcv2(self.fund_perf, self.mkt_perf, self.perf_cut)
        elif self.perf_fee_regime == 'v3':
            self.perfee_rate = perf_fee_calcv3(self.fund_perf, self.mkt_perf, self.perf_cut)
        self.perf_fee = self.perfee_rate * self.client_principal
        self.membership_fee = self.client_principal * self.aum_rate
        self.client_totalfee = self.membership_fee + self.perf_fee
        # CLIENT NET
        self.client_takehome = self.client_grossvalue - self.client_totalfee
        self.client_actualgain = self.client_takehome - self.client_principal
        self.client_actualgainrate = self.client_actualgain / self.client_principal
        # OVERALL PROFIT
        self.revenue = self.client_totalfee * self.num_clients
        self.overall_profit = self.revenue - self.overhead_cost


# generate fund profiles given dict of parameters
def gen_fundprofiles(globalparams):
    your_fund = FundProfile(
        globalparams['your_name'],
        globalparams['client_principal'],
        globalparams['num_clients'],
        globalparams['perf_cut'],
        globalparams['aum_rate'],
        globalparams['mkt_perf'],
        globalparams['your_perf'],
        globalparams['overhead_cost'],
        globalparams['perf_fee_regime']
        )
    comp_fund = FundProfile(
        globalparams['comp_name'],
        globalparams['client_principal'],
        globalparams['comp_num_clients'],
        globalparams['comp_perf_cut'],
        globalparams['comp_aum_rate'],
        globalparams['mkt_perf'],
        globalparams['comp_perf'],
        globalparams['comp_overhead_cost'],
        globalparams['comp_perf_fee_regime']
        )
    mkt_fund = FundProfile(
        'THE MARKET',
        globalparams['client_principal'],
        globalparams['comp_num_clients'],
        0,
        0,
        globalparams['mkt_perf'],
        globalparams['mkt_perf'],
        0,
        'v3'
        )
    return your_fund, comp_fund, mkt_fund


# formats fund
def fundprofile_todict(fund):
    return {
        'PROFILE': fund.profile,
        'client_principal': fund.client_principal,
        'client_takehome': fund.client_takehome,
        'client_grossendvalue': fund.client_grossvalue,
        'mkt_perf': fund.mkt_perf,
        'fund_perf': fund.fund_perf,
        'client_actualgainrate': fund.client_actualgainrate,
        'client_grossgain': fund.client_grossgain,
        'client_actualgain': fund.client_actualgain,
        'membership_fee': fund.membership_fee,
        'perf_fee': fund.perf_fee,
        'client_totalfee': fund.client_totalfee,
        'num_clients': fund.num_clients,
        'fund_revenue': fund.revenue,
        'fund_overhead_cost': fund.overhead_cost,
        'fund_overall_profit': fund.overall_profit,
        'aum_rate': fund.aum_rate,
        'perf_cut': fund.perf_cut,
        'perfee_rate': fund.perfee_rate
    }


# formats fund
def fundprofile_formatnums(fund):
    report = fundprofile_todict(fund)
    for k, v in report.items():
        if k == 'num_clients':
            report.update({k: formalnumber_integer(v)})
        elif k != 'PROFILE':
            p = ['aum_rate', 'perf_cut', 'perfee_rate', 'client_actualgainrate', 'mkt_perf', 'fund_perf']
            if k in p:  # percents
                report.update({k: f'{formalnumber(v*100)} %'})
            elif k not in p:  # dollars
                report.update({k: f'${formalnumber(v)}'})
    return report


# generate dataframe of fund profiles
def gen_fund_df(listofprofiles):
    return pd.DataFrame(data=[fundprofile_formatnums(i) for i in listofprofiles])


# calc edge rate required given competitor's rate and switch factor
def calc_edge_rate(switch_factor, your_fund, comp_fund):
    return abs((comp_fund.client_actualgain * switch_factor) + your_fund.client_totalfee - comp_fund.client_totalfee) / your_fund.client_principal


# returns fund profiles based on comp perf x
def gen_fundprofile_x(new_x, globalparams):
    # EDIT COMP PARAMS
    your_fund = FundProfile(
        globalparams['your_name'],
        globalparams['client_principal'],
        globalparams['num_clients'],
        globalparams['perf_cut'],
        globalparams['aum_rate'],
        globalparams['mkt_perf'],
        globalparams['your_perf'],
        globalparams['overhead_cost'],
        globalparams['perf_fee_regime']
        )
    comp_fund = FundProfile(
        globalparams['comp_name'],
        globalparams['client_principal'],
        globalparams['comp_num_clients'],
        globalparams['comp_perf_cut'],
        globalparams['comp_aum_rate'],
        globalparams['mkt_perf'],
        new_x,
        globalparams['comp_overhead_cost'],
        globalparams['comp_perf_fee_regime']
        )
    return your_fund, comp_fund


# find comprate such that actual rate - (comprate + edgerate) = 0 --> comprate = actual rate - edgerate
def indiff_func(X, globalparams):
    return globalparams['your_perf'] - (X + calc_edge_rate(globalparams['switch_factor'], *gen_fundprofile_x(X, globalparams)))


# returns explanation of what performance rate a competitor fund will need to remain below for the client to switch to you given your fund's performance and switch factor
def explain_compfundperf_boundary(globalparams):
    switch_factor = globalparams['switch_factor']
    comp_perf = globalparams['comp_perf']
    actualedgerate = calc_edge_rate(switch_factor, *gen_fundprofile_x(comp_perf, globalparams))
    indiffpoint = root(indiff_func, args=(globalparams), x0=[0.17])['x'][0]
    your_fund, comp_fund = gen_fundprofile_x(indiffpoint, globalparams)
    checkedgerate = calc_edge_rate(switch_factor, your_fund, comp_fund)
    conclusion = f'The algorithm gave the correct growth rate for {comp_fund.profile} because when plugged back into the formula ({your_fund.profile} rate - (newedgerate + {comp_fund.profile} rate)), it returned a zero (if the following number is a zero, then the algorithm was correct: {your_fund.fund_perf - (checkedgerate + indiffpoint)})' if (your_fund.fund_perf - (checkedgerate + indiffpoint)) == 0 else f'The algorithm somehow was incorrect.  If it were correct, the formula ({your_fund.profile} rate - (newedgerate + {comp_fund.profile} rate)) should equal zero, but instead it equals {your_fund.fund_perf - (checkedgerate + indiffpoint)}.'
    betterorworse = ['better', f'stay with {comp_fund.profile}'] if comp_perf > indiffpoint else ['no better', f'switch over to {your_fund.profile}']
    surpassornot = 'surpassed' if your_fund.fund_perf > comp_perf+actualedgerate else 'failed to surpass'
    return [
        f"Explained in terms of fund performance rates, the client would want to switch over to {your_fund.profile} if {your_fund.profile} experienced a performance growth rate greater than the sum of {comp_fund.profile}'s growth rate and the edge_rate. In this scenario, {your_fund.profile} experienced a growth rate of {formalnumber(your_fund.fund_perf*100)} %.  In contrast, {comp_fund.profile} experienced a growth rate of {formalnumber(comp_perf*100)} %.  Given a switchfactor of {formalnumber(switch_factor*100)} %, this corresponds to an edge rate of {formalnumber(actualedgerate*100)} %.  Adding this to {comp_fund.profile}'s growth rate, we get {formalnumber((comp_perf+actualedgerate)*100)} % as the growth rate {your_fund.profile} would need to beat to win over the client.",
        f"Alternatively, {your_fund.profile} could win over the client if {comp_fund.profile} performs below {formalnumber(indiffpoint*100)} %. Since, in this scenario, {comp_fund.profile} experienced a growth rate of {formalnumber(comp_perf*100)} %, it performed {betterorworse[0]} than {formalnumber(indiffpoint*100)} %. Additionally, {your_fund.profile}'s growth rate of {formalnumber(your_fund.fund_perf*100)} % {surpassornot} the threshold of {formalnumber((comp_perf+actualedgerate)*100)} % required to win over the client.  As a result, the client would {betterorworse[1]}.",
        f"To be sure this calculation is correct, if we plug {formalnumber(indiffpoint*100)} % back into the edgerate formula and add the result to {formalnumber(indiffpoint*100)} %, we should get {formalnumber(your_fund.fund_perf*100)} %.  We get an edge rate of {formalnumber(checkedgerate*100)} %. That new edge rate plus the calculated comp fund rate is {formalnumber((indiffpoint+checkedgerate)*100)} %. {conclusion}."]


# returns explanation of what competitive edge our fund needs to win over a client from competition
def comp_edge_needed(globalparams):
    switch_factor = globalparams['switch_factor']
    your_fund, comp_fund, mkt_fund = gen_fundprofiles(globalparams)
    edge_rate = calc_edge_rate(switch_factor, your_fund, comp_fund)
    edge_rate_actual = your_fund.fund_perf - comp_fund.fund_perf
    edge_rate_actual_mkt = your_fund.fund_perf - mkt_fund.fund_perf
    edge_earnings = your_fund.client_actualgain - comp_fund.client_actualgain

    def switchcompare():
        if your_fund.client_actualgain <= comp_fund.client_actualgain+abs(comp_fund.client_actualgain*switch_factor):
            return f"Since the client would experience an actual gain no better than with {comp_fund.profile} plus the switch factor premium, the client would stay with {comp_fund.profile}."
        else:
            return f"Since the client would experience more actual gains with {your_fund.profile} than the actual gains plus switch factor premium of {comp_fund.profile} (${formalnumber(your_fund.client_actualgain-(comp_fund.client_actualgain+abs(comp_fund.client_actualgain*switch_factor)))} more than the required threshold), the client would switch to {your_fund.profile}."
    return [
        f'CLIENT STARTING CAPITAL: ${formalnumber(your_fund.client_principal)}',
        f'CLIENT ENDING CAPITAL WITH {your_fund.profile}: ${formalnumber(your_fund.client_takehome)}',
        f'CLIENT ENDING CAPITAL WITH {comp_fund.profile}: ${formalnumber(comp_fund.client_takehome)}',
        f'CLIENT ENDING CAPITAL WITH {mkt_fund.profile}: ${formalnumber(mkt_fund.client_takehome)}',
        f'CLIENT GAIN THRU {your_fund.profile}: ${formalnumber(your_fund.client_actualgain)}',
        f'CLIENT GAIN THRU {comp_fund.profile}: ${formalnumber(comp_fund.client_actualgain)}',
        f'CLIENT GAIN THRU {mkt_fund.profile}: ${formalnumber(mkt_fund.client_actualgain)}',
        f'FUND GROWTH RATE - {your_fund.profile}: {formalnumber(your_fund.fund_perf*100)} %',
        f'FUND GROWTH RATE - {comp_fund.profile}: {formalnumber(comp_fund.fund_perf*100)} %',
        f'MARGINAL RATE OVER {comp_fund.profile} REQUIRED TO WIN OVER CLIENT: {formalnumber(edge_rate*100)} %',
        f'ACTUAL MARGINAL RATE ATTAINED OVER {comp_fund.profile}: {formalnumber(edge_rate_actual*100)} %',
        f'ACTUAL MARGINAL RATE ATTAINED OVER {mkt_fund.profile}: {formalnumber(edge_rate_actual_mkt*100)} %',
        f'SWITCH_FACTOR: {formalnumber(switch_factor*100)} %',
        f"{your_fund.profile} experienced a growth rate of {formalnumber(your_fund.fund_perf*100)} % (corresponding client return of ${formalnumber(your_fund.client_actualgain)}) while {comp_fund.profile} experienced a growth rate of {formalnumber(comp_fund.fund_perf*100)} % (corresponding client return of ${formalnumber(comp_fund.client_actualgain)}).  Had client gone with {your_fund.profile} instead of {comp_fund.profile}, they would experience a swing of ${formalnumber(edge_earnings)}.",
        f"WOULD THE CLIENT SWITCH OVER TO {your_fund.profile} IN THESE CIRCUMSTANCES?",
        f"The client would want to switch over to {your_fund.profile} if the client would have made more money going with {your_fund.profile} than with {comp_fund.profile}.  Specifically, the client's actual gain (the amount the client earns after fees) with {your_fund.profile} must be greater than the sum of the client's actual gain with {comp_fund.profile} and an arbitrary premium (the switch_factor).  In this case, the switch_factor is {formalnumber(switch_factor*100)} %, and the client's actual gain with {comp_fund.profile} was ${formalnumber(comp_fund.client_actualgain)}.  Therefore, for the client to switch over to {your_fund.profile}, {your_fund.profile} would need to produce for the client an actual gain greater than ${formalnumber(comp_fund.client_actualgain+abs(comp_fund.client_actualgain*switch_factor))}.",
        f"The actual gain client would have earned with {your_fund.profile} under these circumstances is ${formalnumber(your_fund.client_actualgain)}. {switchcompare()}",
        *explain_compfundperf_boundary(globalparams)
    ]


# return df of coordinates for edgerate as a function of comp perf
def gen_edgeratedf(your_perf, num_datapoints, start_xval, end_xval, globalparams):
    rangeofcomp_perfs = np.linspace(start_xval, end_xval, num=num_datapoints)
    xaxis_name = f'{globalparams["comp_name"]} perfrate'
    graphdf = pd.DataFrame(data={xaxis_name: rangeofcomp_perfs})
    graphdf.reset_index(inplace=True, drop=True)
    graphdf['edgerate needed'] = graphdf[xaxis_name].apply(lambda x: calc_edge_rate(globalparams['switch_factor'], *gen_fundprofile_x(x, globalparams)))
    graphdf['actual_perfrate'] = your_perf
    yaxis_name = f'{globalparams["your_name"]} perfrate needed'
    graphdf[yaxis_name] = graphdf[xaxis_name] + graphdf['edgerate needed']
    graphdf['under/over_performing'] = graphdf['actual_perfrate'] - graphdf[yaxis_name]
    return graphdf


# HOW DOES EDGE RATE CHANGE AS COMP PERF CHANGES WHEN YOUR FUND PERF STAYS CONSTANT?
def graph_edgerate(num_datapoints, start_xval, end_xval, globalparams):
    graphdf = gen_edgeratedf(num_datapoints, start_xval, end_xval, globalparams)

    # GRAPH DF
    graphdf.plot()
    plt.grid()
    plt.show()


# returns fund profiles based on comp perf x and youperf y
def gen_fundprofile_xy(new_x, new_y, globalparams):
    # EDIT COMP PARAMS
    your_fund = FundProfile(
        globalparams['your_name'],
        globalparams['client_principal'],
        globalparams['num_clients'],
        globalparams['perf_cut'],
        globalparams['aum_rate'],
        globalparams['mkt_perf'],
        new_y,
        globalparams['overhead_cost'],
        globalparams['perf_fee_regime']
        )
    comp_fund = FundProfile(
        globalparams['comp_name'],
        globalparams['client_principal'],
        globalparams['comp_num_clients'],
        globalparams['comp_perf_cut'],
        globalparams['comp_aum_rate'],
        globalparams['mkt_perf'],
        new_x,
        globalparams['comp_overhead_cost'],
        globalparams['comp_perf_fee_regime']
        )
    return your_fund, comp_fund


# return edge rate when input custom comp perf and you perf figures
def edgerate_unknownxy(new_x, new_y, globalparams):
    return calc_edge_rate(globalparams['switch_factor'], *gen_fundprofile_xy(new_x, new_y, globalparams))


def graph_edgerate3d(num_datapoints_x, start_xval, end_xval, num_datapoints_y, start_yval, end_yval, globalparams):
    xaxlabel = globalparams['comp_name']
    yaxlabel = globalparams['your_name']
    zaxlabel = 'edge_rate_needed'
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    X = np.linspace(start_xval, end_xval, num=num_datapoints_x)
    Y = np.linspace(start_yval, end_yval, num=num_datapoints_y)
    X, Y = np.meshgrid(X, Y)
    vectedgerate = np.vectorize(edgerate_unknownxy, excluded=['globalparams'])
    Z = vectedgerate(globalparams=globalparams, new_x=X, new_y=Y)
    ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
    ax.set_ylabel(yaxlabel)
    ax.set_xlabel(xaxlabel)
    ax.set_zlabel(zaxlabel)
    plt.show()
