# Proto app of transcribing text from images

The app runs series of image recognition tasks.
Player should recognize distorted text on image and respond with text answer.

The game is limited in number of trials, allowed number of failures, and page timeout.

## Workflow

- predefined number of random trials are generated on session creation
- the trials are sequentially displayed to a player
- player responds with their answer
- the answer is validated on server and feedback is given
- score is assigned for each correct or incorrect answer
- then page iterates to next trial

## Interface

- each task is shown as a big image on screen
- player gives response by typing into a text field and pressing 'Enter'
- validity of an answer is indicated by highlighting the input field
- feedback is shown with resulting score for each trial
- overall progress is indicated by nice animated progress bar

## Features

- trials are generated randomly
- images are generated from texts and saved as binary data
- response time is measured
- all data is recorded for each trial
- series are terminated when player reloades page or navigates back/forth
