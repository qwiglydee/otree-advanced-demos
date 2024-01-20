# otree-advanced-demos

The project presents a bunch of prototypical web applications for behaviorial or psycological online experiments, surveys or tests.
The apps are developed using [oTree](www.otree.org) framework and it's new (upcoming) extension <b>oTree-front</b> (shipped in this repository)

The apps implement some basic functionality and intentionally designed to be adjustable for some futher requirements.
They may be useful in your research projects as a starting point of your app.

The repository also contains bunch of snippets (python utilities, javascripts, styles) that can be reused in any other project unrelated to the apps.

See [USAGE](USAGE.md) for guides how to use the apps or snippets in your project.

## Features

- Main pages of the apps are implemented in a dynamic manner for real-time interaction with low latency.
  (Contrary to traditional form-based approach that require full page reload).
- Most of the apps run series of trials consisting of some task and expecting some response.
- Responses of participants are immediately communicated and saved on server via live channel.
- All the data for each trial is saved and available in 'custom export' section.
- Where appropriate, pages measure response time with high precision (below 15ms), not affected by network latency.
- The pages are designed in smooth animated styles, reducing visual disturbances.
- The pages do not reveal correct or best answers, all evaluation of responses is performed on server side. That reduces possibility of cheating via inspecting page scripts and content.

## Apps

For detail, navigate into subdirectory of corresponding app.

- [simple](simple): Pregenerated series of simple trials with text task and text input
- [choices](choices): Trials with answer choices on buttons.
- [choices2](choices2): Trials with answer choices on radio buttons with a submit button.
- [infinite](infinite): Infinite series of simple trials, generated on demand.
- [timers](timers): Infinite series with animated timers for page and response timeouts.
- [phases](phases): Trials with several time-based phases.
- [multistep](multistep): Trials with several sequential input steps.
- [multistage](multistage): Trials with several irregular or conditional stages.
- [captcha](captcha): Trials with images generated from text.
- [drawing](drawing): Trials with images and free-hand drawing input.
- [sliders](sliders): Classic slider tasks, with real-time feedback.
- [voting](voting): Group voting with online chat.

## Snippets

For detail, navigate into corresponding source file.

- **csv** [python utils](utils/csv.py): to load, filter, sample data from csv files
- **images** [python utils](utils/images.py): to generate and encode images with text
- **pagetime** [python utils](utils/pagetime.py): to track time spent on pages (server-side)
- **rnd** [python utils](utils/rnd.py): few simple random functions
- **fullscreen** [styles](_static/fullscreen.css): for full-screen pages with auto-centered content
- **ot-progress** [scripts](_static/ot-progress.js) and its [styles](_static/ot-progress.css): a directive to display nice animated progress bar
- **ot-pulse** [scripts](_static/ot-pulse.js) and its [styles](_static/ot-pulse.css): a directive to show pulsating dots for "waiting" periods
- **ot-stage** [scripts](_static/ot-stage.js): a directive and utility to dynamically switch fragments of a page
- **score** [scripts](_static/format_score.js): few simple functions to format text like "N points"
- **live** [back-end](utils/live.py), [front-end](_static/otree-front-live.js): message-oriented protocol of live server/page communication
- [otree-front-ext.js](_static/otree-front-ext.js): some useful utilities for otree-front
- [otree-front-ext.css](_static/otree-front-ext.css): some style enhancments

# Support

You can support this initiative by making some donation in crypto currency - BTC:`bc1q55dmnurjj4c7s2wy2k4dr8swnjk8ypd49w8964`
or ETH:`0xF0FAAeA5c9DFF2ca1eaA946FB71c89432983f2Ce`

You can also hire me to assist in your project with web development.
Conact me via `qwiglydee@gmail.com`, or by the same nickname in Telegram or WhatsApp.
