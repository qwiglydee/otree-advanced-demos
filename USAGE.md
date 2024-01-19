# otree-advanced-demos

## Apps

To use an app as a starting code base in your project:
- download the code (from Releases section) and unpack somewhere
- copy directory of desired app into your progect
- copy full directoties `_static` and `utils` into your project
- add the app into the `settings.py`
- adjust code of the app to fit your needs

## Python utils

To reuse a python snippet:
- copy `.py` files into `utils` subdirectory in your project
- import the module in `__init__.py` of your app:
  ```python
  from utils import something
  ```

## Javascripts

Main library is the `otree-front-xxx.js`, it should be included for most other stuff to work.
In some future releases of oTree it may come automatically included into all pages.

To reuse a javascript snippet:
- copy desired `.js` files into `_static` subdirectory in your project
- in a template of a page, include the script into script block:
  ```html
  {{ block scripts }}
  <script src="{{ static 'otree-front-2.0.0.b2.js' }}"></script>
  <script src="{{ static 'something.js' }}"></script>
  {{ endblock }}
  ```

Some snippets also need corresponding styles to be loaded.

## Styles

To reuse a style snippet:
- copy desired `.css` file into `_static` subdirectory in your project
- in a template of a page, include the styles in styles block:
  ```html
  {{ block styles }}
  <link rel="stylesheet" href="{{ static 'something.css' }}">
  {{ endblock }}
  ```

Some styles are adjustable for particular pages or even elements via css variables (you can see them in the css files as `--ot-something`)
To adjust the variables, insert style section in styles block (after links) and define variables in rules for `:root` (for all page) or a specific element:

```html
<style>
:root {
    --ot-fade-out-time: 100ms;
}

section.some_class {
    --ot-fade-out-time: 200ms;
}
</style>
```
