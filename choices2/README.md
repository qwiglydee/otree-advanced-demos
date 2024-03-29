# Proto app of trials with choices

The app runs series of math tasks. Player should select correct answers from provided options.
Condition for each player determines if numbers in the expressions are all odd, even or mixed.

The game is limited in number of trials, allowed number of failures, and page timeout.

![screenshot](../_screenshots/choices2.png)

## Workflow

- predefined number of random trials are generated on session creation along with answer options for each trials
- the trials are sequentially displayed to a player
- player responds with their answer choosen from provided options
- player can change their answer before submitting
- the answer is validated on server and feedback is given
- score is assigned for each correct or incorrect answer
- then page iterates to next trial

## Interface

- player gives response by selecting a radio button with an answer and then pressing 'Submit'
- validity of an answer is indicated by highlighting the selected radio button
- overall progress is indicated by nice animated progress bar
- feedback is shown with resulting score for each trial

## Features

- trials are generated randomly
- response time is measured
- all data is recorded for each trial
- series are terminated when player reloades page or navigates back/forth
