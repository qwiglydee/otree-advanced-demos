# Sliders

Classic sliders task.

The objective is to put all sliders on page into middle position.

- page shows N sliders with random offset and random initial position
- user should move slider handle
- each move is validated on server, and solved sliders are highlighted
- score is calculated for every move
- the page terminates when all sliders are solved or page timeout happens

Live interaction scheme:
- data for sliders is stored in separate data model individually
- sliders are pregenerated for a session and embedded into the page when it's loaded
- every slider move is saved to server in real time
- sliders are validated (on server) and highlighted when correct
- results for all sliders are available via custom export
- the page is generally tolerant to reloading and navigating out

Drawbacks:
- the page is vulnerable to cheating