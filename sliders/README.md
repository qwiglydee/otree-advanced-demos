# Proto app of sliders task

The app runs classic sliders task.
Player should move handles of all sliders in their middle position.

The game is limited by page timeout.

## Workflow

- predefined number of slider with random shifts are generated on session creation
- all the sliders are displayed to a player
- player moves handles of the sliders
- each move is immediately evaluated on server
- score is assigned for each move

## Interface

- sliders are randomly shifted
- validity of each slider is indicated by color of the handle
- overall progress is indicated by nice animated progress bar

## Features

- aliders are generated randomly
- state of each slider is saved
- when player reloades page aliders restore their state