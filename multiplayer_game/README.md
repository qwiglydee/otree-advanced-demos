# Multiplayer Game

The task is just to type anything in a limited time.

Players who close their browser or hesitate for too long get dropped out from the game.

The app is divided into two parts:
- [screener](../multiplayer_screener): the screener part
- [game](../multiplayer_game): this is the main part


## Workflow

- Participants answer some questions in a separate screener app.
- Those who close the screener app are just ignored.
- Those who passes to the main app get grouped (by 2 or any other number).
- Participants just type any text.
- Those who wait too long get dropped out by page timeout and end up on a dead-end page.
- Those who close browser after the game started get dropped out.
- Payoff is a group bonus fund divided among players who left.

## Features

- separate screener app
- regrouping participants by arrival time
- importing data from the screener app
- waiting for all players to complete the task at a checkin page
- detecting and dropping out participants who wait too long
- detecting and dropping out participants who closed browser

## Misfeatures

With incoordinate timeouts it may happen that some participants complete the game page after the first participant already passed the waiting page and marked all group as passed. The situation results in an error "participant way too late".
Workaround is to set up wait timeout larger than game timeout.
