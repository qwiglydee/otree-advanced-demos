> :warning: work in progress

# otree-advanced-demos

Apps and snippets for [oTree](https://www.otree.org/) (v5) using some advanced techniques.

All the interactive pages constructied with [otree-front](https://github.com/qwiglydee/otree-front) (v1.5.beta) micro-framework

# Features

- most apps run on live pages with realtime communication
- trials are stored in separate data model
- results for all trials are available via custom export
- precise response time (ms) is measured and recorded
- correct answers are not revealed to pages (except in feedback) making the game cheater-proof
- the pages are generally tolerant to reloading or navigating out (except reloading while network failure)

# Apps

- [live trials](trials_live): running series of pregenerated trials on a live page
- [infinite trials](trials_inf): running series of trials generated on demand
- [captcha](captcha): transcribing math from image with distorted font
- [drawing](drawing): free-hand drawing input
- [sliders](sliders): sliders task with realtime feedback
- [voting](voting): real-time chat and group voting
- [phases](phases): timer-scheduled phases of trials

# Utils

- [live utils](utils/live_utils.py): for advanced live real-time comunication with pages
- [csv utils](utils/csv_utils.py): to load data from csv with filtering/sampling/etc
- [image utis](utils/image_utils.py): to generate and encode some simple images
- [pagetime](utils/pagetime.py): to track time spent on pages

