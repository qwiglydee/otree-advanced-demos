> :warning: work in progress

# otree-advanced-demos

Apps and snippets for [oTree](https://www.otree.org/) (v5) using some advanced techniques.

All the interactive pages constructied with [otree-front](https://github.com/qwiglydee/otree-front) (v1.3.beta1) micro-framework

# Features

- nice progress bar created with the micro-framework
- some style enhancements
- apps do not reveal correct/best answers on pages making them cheater-proof
- some apps communicate responses to server in real time to reduce data loss

# Apps

- [live trials](trials_live): running series of trials on page with live communication
- [infinite trials](trials_infinite): running infinite series of trials generated on demand
- [local trials](trials_local): running series of trials without live communication
- [sliders](sliders): classic sliders real effort task
- [captcha](captcha): transcribing distorted text from images, which are generated on demand

# Utils

- [live utils](utils/live_utils.py): for advanced live real-time comunication with pages
- [pagetime](utils/pagetime.py): to track time spent on pages
- [csv utils](utils/csv_utils.py): to load data from csv with filtering/sampling/etc
- [image utis](utils/image_utils.py): to generate and encode some simple images
