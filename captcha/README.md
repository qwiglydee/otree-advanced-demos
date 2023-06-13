# Captcha

Runs series of trials on page using [infinite iteration scheme](trials_infinite)

The tasks is to transcribe text from distorted images.

- problem is an image with distorted text, generated dynamically on demand
- response is entered into a text input field
- feedback is shown for every response
- score is calculated for every response
- series terminate when page timeout occurs

Drawbacks:
- images occupy huge space in database and exported data