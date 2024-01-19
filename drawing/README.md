# Proto app of free-hand drawing

The app runs series of hand-drawing tasks.
Player should reproduce an emoji they see in each task.

The game is limited in number of trials and page timeout.

## Workflow

- predefined number of random trials are generated on session creation
- the trials are sequentially displayed to a player
- player responds by free-hand drawing or skips a trial
- the drawing is recorded on server
- score is assigned for each drawn or skipped image
- then page iterates to next trial

## Interface

- player gives response by drawing on a canvas and then pressing 'Submit'
- feedback is shown with resulting score for each trial
- overall progress is indicated by nice animated progress bar

## Features

- trials are generated randomly
- response time is measured
- players' drawings are saved as binary data
- all data is recorded for each trial
- series are terminated when player reloades page or navigates back/forth
