# Proto app of simple trials

The app runs series of math tasks. Player should calculate expressions and respond with correct answers.
Condition for each player determines if numbers in the expressions are all odd, even or mixed.

The game is limited in number of trials, allowed number of failures, and page timeout.

## Workflow

- predefined number of random trials are generated on session creation
- the trials are sequentially displayed to a player
- player responds with their answer
- the answer is validated on server and feedback is given
- score is assigned for each correct or incorrect answer
- then page iterates to next trial

## Interface

- player gives response by typing into a text field and pressing 'Enter'
- validity of an answer is indicated by highlighting the input field
- feedback is shown with resulting score for each trial
- overall progress is indicated by nice animated progress bar

## Features

- trials are generated randomly
- response time is measured
- all data is recorded for each trial
- series are terminated when player reloades page or navigates back/forth