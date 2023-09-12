# Sliders

Classic sliders task.

The objective is to put all sliders on page into middle position.

Player should drag slider handle or use keyboard.

Each move is evaluated to gain score.

Workflow:
- sliders are pregenerated during session initialization
- sliders are embedded into page when it's reloading
- each move is sent to server for evaluation
- score calculated for each move
- feedback is reported for every slider after every move to indicate status