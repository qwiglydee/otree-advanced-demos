# Local Trials

Runs series of trials on page.
The tasks are simple math expressions to solve.

- data for trials is stored in separate data model individually
- trials are pregenerated for a session and embedded into the page when it's loaded
- not revealing correct answers to the browser to make pages cheater-proof
- iteration loop is run by on-page scripts
- responses are submitted via hidden form field
- total time on page is measured
- results for all trials are available via custom export

Drawbacks:
- data is lost when navigating page out, reloading/back/forth
- no answer validation (because correct answers are not available)