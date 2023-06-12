# Infinite Trials

Runs series of trials on page.
The tasks are simple math expressions to solve.

- data for trials is stored in separate data model individually
- trials are generated on demand on back-end
- not revealing correct answers to the browser to make pages cheater-proof
- iteration loop is run by server and synchronized with page
- responses are sent to server in real time
- responses are validated (on server) and feedback is shown for every response
- measuring precise reaction time of every response
- results for all trials are available via custom export
- the page is generally tolerant to reloading and navigating out

Drawbacks:
- iteration loop may stuck over unstable network connection
- which can provoke users to reload page or navigating out, and backing off iteration loop