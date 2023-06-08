> :warning: work in progress

# otree-advanced-demos

Apps and snippets for oTree (v5) using some advanced techniques.

All the interactive pages constructied with [otree-front](https://github.com/qwiglydee/otree-front) micro-framework

# Features

- nice progress bar created with the micro-framework
- some style enhancements
- smooth trial transitions
- apps do not reveal cirrect/best answers on pages making them cheater-proof

# Utils

- [live utils](utils/live_utils.py): for advanced live real-time comunication with pages
- [pagetime](utils/pagetime.py): to track time spent on pages
- [csv utils](utils/csv_utils.py): to load data from csv with filtering/sampling/etc
- [image utis](utils/image_utils.py): to generate and encode some simple images

# Apps

- [local trials](trials_local): running series of trials on page (no live communication)
- [live trials](trials_live): running series of trials on page with live communication
- [infinite trials](trials_infinite): running infinite series of trials generated on demand