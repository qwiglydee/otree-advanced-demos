# Captcha

Runs series of trials on page.
The tasks is to transcribe text from distorted images.

Using 'infinite series' scheme.

- data for trials is stored in separate data model individually
- images are generated on demand on back-end
- not revealing correct answers to the browser to make pages cheater-proof
- iteration loop is run by server and synchronized with page
- responses are sent to server in real time
- responses are validated (on server) and feedback is shown for every response
- measuring precise reaction time of every response
- results for all trials are available via custom export
- the page is generally tolerant to reloading and navigating out

Drawbacks:
- images occupy huge space in database and exported data