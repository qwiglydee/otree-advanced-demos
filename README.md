# otree-advanced-demos

Apps for oTree platform using some advanced techniques and `otree-front` microframework.

# Trials apps

Various apps consisting of iteration over trials and receiving responses.
The trials are expressions like "NN + NN" and responses are evaluation of the expressions.
Score is calculated by number of correct answers.

Features:
- all the trials are saved in database and exported via 'custom export'
- correct answers are not disclosed in the page, so cheaters cannot exploit any scripts
- restoring progress on page reload
- calculating total score
- fullscreen layout
- smooth progress bar
- smooth trial switching
- measuring reaction time (or task time)
- showing feedback

## `trials_form`

An app for very small set of trials and simple answers.

- trials are pre-generated and embedded into page
- iterating runs by on-page scripts
- responses are stored in hidden form field
- not restoring progress on reload
- no feedback

## `trials_live`

An app for a sequence of trials with server-side validation.

- trials are pre-generated and embedded into page
- iterating runs by on-page scripts with confirmations from server
- progress is synchronized with server and restored when page reloaded
- responses are communicated to server for validation and saving

## `trials_stream`

An app for infinite or non-linear sequence of trials.

- trials are generated on demand for each iteration
- iterating runs on server
- progress is controlled by server and restored when page reloaded
- responses are communicated to server for validation and saving

## `trials_buttons`

The app provides labeled choices 'A/B/C' for answers.
Layout is randomized for every player.
Resposes are recorded with selected label, its position and value.

Based on `trials_live`

## `trials_choices`

The app provides list of choices for answers.
Layout is randomized for every trial.
Resposes are recorded with its position and value.

Based on `trials_live`
