# otree-advanced-demos

Apps for oTree platform using some advanced techniques and `otree-front` microframework. 

# Trials apps

Various apps consisting of iteration over trials and receiving responses. 

All the trials are saved in database as `ExtraModel` and can be exported via 'custom export'

Correct answers are not disclosed in the page, so that cheaters can exploit any scripts

Live pages restore their current state when reloaded.

In the demos all trials are expressions like "NN + NN" and responses are evaluation of the expressions. 
Score is calculated by number of correct answers.

- `trials_basic`: basic app, small number of trials, iterating runs on-page, results saved in hidden fields, no feedback
- `trials_choices`: basic app with answers selected from randomized choices, no feedback
- `trials_halflive`: live page app, communicates with server to validate responses and provide feedback
- `trials_live`: live page app, iterating runs fully on server, communicating progress, trials, responses, feedback
- `trials_infinite`: live page app with time limit, generating trials on demand in an infinite sequence  
