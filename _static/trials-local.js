/** Minimalistic implementation of live trials iteration
 *
 * Iteration loop run by on-page scripts.
 * Trials data is embedded into page (via js_vars).
 * Responses are submitted via hidden form field.
 *
 * Control flow:
 * - resetting progress
 * - iterating from start
 * - showing current trial
 * - taking response from user
 * - saving the response to buffer
 * - continuing loop or completing page
 * - iterating loop or completing page
 * - before completing: serializing responses as json into 'vars.responses_json'
 *
 * Constants used:
 * - TRIALS: pre-generated trials in form { iteration: trial_data, ... }
 * - TRIAL_DELAY: delay in ms after trial completed
 *
 * Page vars used:
 * - vars.progress: { total, competed, iteration }
 * - vars.trial: current trial data form TRIALS
 * - vars.response: response, should be provided by ot.completeTrial({ response: ... })
 *
 * Features:
 * - soft transition
 *   - vars.transition: "fadeout" or "fadein" css class
 *   - FADEOUT_TIME: should be time of the animation in ms
 */

function fadeout() {
    vars.transition = "fadeout";
}

function fadein() {
    vars.transition = "fadein";
}

const responses_buffer = [];

ot.onStartPage(function () {
    // initialize progress
    vars.progress = {
        total: Object.entries(TRIALS).length,
        completed: 0,
        iteration: 0,
    }

    // a buffer of all responses to put into a form field
    vars.responses_json = "";

    ot.nextIteration();
});

ot.onNextIteration(function () {
    // complete loop if iteration is over
    if (vars.progress.completed == vars.progress.total) {
        ot.completePage();
        return;
    }

    // advance the loop
    vars.progress.iteration = vars.progress.completed + 1;

    // get trial data and run it
    ot.startTrial(TRIALS[vars.progress.iteration]);
});

ot.onStartTrial(function (trial) {
    // reset trial-related data
    vars.trial = trial;
    vars.response = null;
    vars.feedback = null;

    fadein();

    ot.showDisplays();
    ot.resetInputs();
    ot.enableInputs();
});

ot.onCompleteTrial(function (result) {
    // prevent extra input
    ot.disableInputs();

    // put response on page
    vars.response = result.response;

    // keep response in buffer
    responses_buffer.push(result.response);

    ot.completeIteration();
});

ot.onCompleteIteration(function() {
    // advance the progress
    vars.progress.completed += 1;

    ot.delay(TRIAL_DELAY - FADEOUT_TIME, fadeout);
    ot.delay(TRIAL_DELAY, ot.nextIteration);
});

/* before submitting the page  */
ot.onCompletePage(function () {
    // save responses into form field
    vars.responses_json = JSON.stringify(responses_buffer);
});