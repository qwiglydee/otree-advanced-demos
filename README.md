> :warning:
> The project is still under development and not perfectly tested.

# otree-advanced-demos

The project presents a bunch of prototypical web applications for behaviorial or psycological online experiments, surveys or tests.

They may be useful in your research projects as a starting point of your app.
You copy some of the app that best matches your experiment design and adjust code to fit your needs.

The apps are developed using [oTree](www.otree.org) framework and it's new (upcoming) extension `otree-front.js` (shipped in this repository)

## Features

- Main pages are implemented in a dynamic manner for real-time interaction with low latency.
  (Contrary to traditional form-based approach that require full page reload).
- Responses are immediately communicated and saved on server via live channel.
- Where appropriate, pages measure response time with high precision (about 15ms), not affected by network latency.
- The pages are designed in smooth animated styles, reducing visual disturbances.
- The pages do not reveal correct or best answers, reducing possibility of cheating via inspecting page scripts and content.
  Evaluation of answrs is performed on server side.
- The apps detect and prohibit page reloading on the page of tasks, to protect data and measurements from users or browsers misbehavior.
- The code contains double-checking of data to ease detecting bugs during development.

## Apps

Most apps run series of trials consisting of a task and expecting a solution in response.
Detailed data for each trial is saved in additional data models and can be exported via 'custom export' feature.

- [simple](simple): Pregenerated series of simple trials with text task and text input
- [simple2](simple2): Trials with multiple inputs and a submit button.
- [stages](stages): Trials with several different conditional stages.
- [choices](choices): Trials with answer choices on buttons.
- [choices2](choices2): Trials with answer choices on radio buttons with a submit button.
- [infinite](infinite): Infinite series of simple trials, generated on demand.
- [timers](timers): Infinite series with animated timers for page and response timeouts.
- [phases](phases): Trials with several time-based phases.
- [captcha](captcha): Trials with images generated from text.
- [drawing](drawing): Trials with images and free-hand drawing input.
- [sliders](sliders): Classic slider tasks, with real-time feedback.
- [voting](voting): Group voting with online chat.

## Snippets

The snippets are pieces of code for either back-end (python) or front-end (javascript) and styles (css)
that can be attached and reused in any other otree app or a particular page.

- csv utils [(back)](utils/csv.py): to load, filter, sample data from csv files
- image utils [(back)](utils/images.py): to generate and encode images
- pagetime utils [(back)](utils/pagetime.py): to track time spent on pages
- live utils [(back)](utils/live.py), [(front)](_static/otree-front-live.js): to simplify and enhance message-oriented live communication.
- fullscreen [(styles)](_static/fullscreen.css): for full-screen pages with auto-centered content
- progress bar [(front)](_static/ot-progress.js), [(styles)](_stativ/ot-progress.css): a directive to display nice animated progress bar
- various enhancements [(front)](_static/otree-front-ext.js), [(styles)](_static/otree-front-ext.css):
  - some helpers to install handlers of `ot.onEvent` and for built-in oTree page timer
  - some adjustments for form input styles
  - directive `ot-fade` to make smooth transitions of main page areas
  - directive `ot-switch` to make smooth switching between page fragments
  - directive `ot-dim` to make hidden parts look dimmed instead of completely hiding
  - directive `ot-pulse` to display pulsating dots to indicate "waiting" pauses

## Usage

To use an app as a starting code base in your project:
- download the code (from Releases section) and unpack somewhere
- copy directory of desired app into your progect
- copy full directoties `_static` and `utils` into your project
- add the app into the `settings.py`
- adjust code of the app to fit your needs

To reuse a python snippet:
- copy `.py` files into `utils` subdirectory in your project
- import the module in `__init__.py` of your app:
  ```python
  from utils import something
  ```

To reuse a javascript snippet:
- copy desired `.js` files into `_static` subdirectory in your project
- in a template of a page, include the script into script block:
  ```html
  {{ block scripts }}
  <script src="{{ static 'something.js' }}"></script>
  {{ endblock }}
  ```

To reuse a style snippet:
- copy desired `.css` file into `_static` subdirectory in your project
- in a template of a page, include the styles in styles block:
  ```html
  {{ block styles }}
  <link rel="stylesheet" href="{{ static 'something.css' }}">
  {{ endblock }}
  ```
- some styles are adjustable for particular pages via css variables
  (you can see them in the css files as `--ot-something-something`)
- to adjust styles for a page or a particular element, insert style variables into the same styles block, after `link`s:
  ```html
  <style>
    :root {
        --ot-dim-opacity: 0.25;
    }

    section[ot-dim] {
        --ot-dim-opacity: 0.75;
    }
  </style>
  ```

# Support

You can support this initiative by making some donation in crypto currency - BTC:`bc1q55dmnurjj4c7s2wy2k4dr8swnjk8ypd49w8964`
or ETH:`0xF0FAAeA5c9DFF2ca1eaA946FB71c89432983f2Ce`

You can also hire me to assist in your project with web development.
Conact me via `qwiglydee@gmail.com`, or the same nickname in Telegram or WhatsApp.


