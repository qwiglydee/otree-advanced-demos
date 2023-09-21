# Simple Trials

The task is to solve a simple math expression.

## Workflow

- The tasks are randomly pre-generated for each player when session is initialized.
- Task is given as plain text on the page
- Answer is taken from text input field
- The answer is evaluated and score is assigned for correct and incorrect answers
- If the answer is 0 it is not accepted and more retries are allowed
- Feedback is given for each trial, including correct answer and resulting score
- Trial sequence automatically advances after some delay
- The page completes when all trials are completed or the page timeouts

## Features

- pre-generating all trials
- basic dynamic content on the page
- native text input field
- key input (for handling 'Enter')
- measuring response time
- custom widget for progress