# Proto app of infinite trials

The app runs series of math tasks. Player should calculate expressions and respond with correct answers.
Condition for each player determines if numbers in the expressions are all odd, even or mixed.

The game is not limited in number of trials, but ony limited in allowed number of failures, and page timeout.
Player is limited in time to solve each task.

## Workflow

- random trials are generated on demand as player is running the series
- the trials are sequentially displayed to a player
- player responds with their answer
- the answer is validated on server and feedback is given
- score is assigned for each correct or incorrect answer, or a trial timeout
- then page iterates to next trial

## Interface

- player gives response by typing into a text field and pressing 'Enter'
- validity of an answer is indicated by highlighting the input field
- feedback is shown with resulting score for each trial
- overall remaining time is indicated by nice animated progress bar
- time remaining for each trial is indicated by another animated bar


## Features

- trials are generated randomly
- response time is measures
- all data is recorded for each trial
- series are terminated when player reloades page or navigates back/forth