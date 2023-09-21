# Phases

The task is to decide if math expressions are correct, in very limited time.

Each trial is scheduled into phases:

1. aiming with a cross in center
2. short exposure of the stimuus (the task expression)
3. some time to response
4. when time runs out trial completes with failure

## Workflow

- The tasks are randomly pre-generated for each player when session is initialized.
- Trial is displayed according to scheduled phases
- Answer is taken from keypress 'Y' or 'N'
- If an answer is not given in scheduled time, trial is failed.
- The answer is evaluated and score is assigned for correct, incorrect answers, or timeouted trials.
- Feedback is given for each trial, including correct answer and resulting score
- Trial sequence automatically advances after some delay
- The page completes when all trials are completed or the page timeouts


## Features
- scheduling phases
- response timeout
- input from keypresses
- measuring response time
