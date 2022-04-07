from Modules.numbers import formalnumber


def strattest_sequential_final_report(bp):
    return [
        f"Overall, had you gone with this strategy from {bp['startdate']} to {bp['enddate']}, investing in {bp['num_periods']} periods of {bp['investperiod']} days each, your capital would have gone from ${formalnumber(bp['startcapital'])} to ${formalnumber(bp['endcapital'])}, an overall growth rate of {formalnumber(bp['growthrate_overall']*100)} %, or ${formalnumber(bp['growth_capital_overall'])} overall. This would translate to an effective investment period growth rate of {formalnumber(bp['effective_period_growthrate']*100)} % per investment period.",
        f"In contrast, had you put your money in {bp['benchmark']} instead, your capital would have gone from ${formalnumber(bp['startcapital'])} to ${formalnumber(bp['endcapital_bench'])}, an overall growth rate of {formalnumber(bp['growthrate_bench_overall']*100)} %, or ${formalnumber(bp['growth_capital_bench_overall'])} overall. This would translate to an effective investment period growth rate of {formalnumber(bp['effective_period_growthrate_bench']*100)} % per investment period.",
        f"Therefore as a result of using the strategy, your portfolio therefore would have experienced a marginal rate over {bp['benchmark']} of {formalnumber(bp['growthrate_margin_overall']*100)} %, a difference of ${formalnumber(bp['endcapital_margin_overall'])}.",
        f"Out of a total {bp['num_periods']} periods, {bp['benchmark']} had a growth rate above 0% {bp['abovezerotally_bench']} time(s) ({formalnumber((bp['abovezerotally_bench'] / bp['num_periods'])*100)} %) whereas the strategy had it {bp['abovezerotally']} time(s) ({formalnumber((bp['abovezerotally'] / bp['num_periods'])*100)} %).",
        f"Out of a total {bp['num_periods']} periods, your portfolio had a growth rate above {bp['benchmark']} {bp['abovebench_tally']} time(s) ({formalnumber((bp['abovebench_tally'] / bp['num_periods'])*100)} %).",
        f"Out of a total {bp['num_periods']} periods, your portfolio had a positive growth rate above {bp['benchmark']} {bp['abovebench_pos_tally']} time(s) ({formalnumber((bp['abovebench_pos_tally'] / bp['num_periods'])*100)} %).",
        f"Overall runtime for this test: {bp['runtime']} secs."
        ]
