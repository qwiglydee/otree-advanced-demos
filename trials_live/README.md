# Live Trials

The task is to solve simple math expressions.
The expressions are generated randomly.

Response is entered into text field.

Score is updated for successes and failures.

Workflow:
- trials are pregenerated during session initialization
- trials are retrieved from server one by one
- responses are sent to server for each trial
- responses are validated and evaluated on server
- score calculated for each trial
- feedback is shown for every response
- answer 0 is not accepted and more retries allowed
- series terminate when all trials completed or after N failures