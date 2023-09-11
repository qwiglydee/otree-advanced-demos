# Drawing

The task is to solve simple math expressions. The expressions are generated randomly.

Response is hand-drawn on a canvas.

Response images are analized for painted area, scarse painted answers not accepted.

Workflow:
- the same as of [`trials_live`](../trials_live)
- response images are encoded and saved as "data-urls" into database

Drawbacks:
- images occupy huge space in database and exported data