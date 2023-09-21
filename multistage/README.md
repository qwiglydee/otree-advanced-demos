# Multistage Trials

The task is to solve a simple math expression using different strategies.

The task is of 2 variable stages:
1. player selects a strategy: 'choose', 'skip', '50:50'
2. depends on selected strategy:
  - 'choose': player selects an option with their answer
  - '50:50': half of options are disabled, player selects an option from remaining
  - 'skip': the trial is completed without an answer

## Workflow

- Basically, the same as of `trials_choices`
- Strategy is selected from predefined choices.
- Available options may change in response of the strategy
- Answer is selected from provided options.
- The answer is evaluated and score is assigned for correct and incorrect answers,
  with defined penalty of using 'skip' or '50:50
- Trial sequence advances manually by 'continue' button available after feedback

## Features

- conditional workflow
- multiple input fields and partially complete trials
- restoring trial state when page is loaded
- switching input fields and page fragments according to active stage