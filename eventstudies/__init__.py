"""Project3 Event Studies -- index-level event and calendar studies with placebo inference."""
from .core import (align_dates, calendar_month_table, event_paths, monthly_returns, paired_t,
                   permutation_diff, placebo_path_band, placebo_pvalue, placebo_window_means,
                   sell_in_may_table, us_election_dates, us_election_day, welch_t, window_returns)

__all__ = ["align_dates", "calendar_month_table", "event_paths", "monthly_returns", "paired_t",
           "permutation_diff", "placebo_path_band", "placebo_pvalue", "placebo_window_means",
           "sell_in_may_table", "us_election_dates", "us_election_day", "welch_t", "window_returns"]
