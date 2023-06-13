# Infinite Trials

Runs series of trials on page.

The task is about solving simple math expressions.
- problem is a math expression, generated randomly for each player
- response is entered in text input field
- feedback is shown for each trial
- score calculated for each trial
- series terminate after N failures

Infinite iteration scheme:
- data for trials is stored in separate data model individually
- trials are generated on demand on back-end
- not revealing correct answers to the browser to make pages cheater-proof
- iteration loop is run by server and synchronized with page
- responses are sent to server in real time
- responses are validated (on server) and feedback is shown for every response
- measuring precise reaction time of every response
- results for all trials are available via custom export
- the page is generally tolerant to reloading and navigating out

Features:
- nice progress bar
- smooth trials transition (**NOTE**: that affects reaction time measurement for 50ms)

Drawbacks:
- iteration loop may stuck over unstable network connection
- which can provoke users to reload page or navigating out, and backing off iteration loop