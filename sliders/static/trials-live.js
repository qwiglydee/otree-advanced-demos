/** Generic implementation of live trials iteration
 *
 * Iteration loop run by on-page scripts, synchronized with server.
 * Trials data is embedded into page.
 * Responses are send to server in real-time.
 *
 * Control flow:
 * - notifying server when page started
 * - receiving current/initial state of progress
 * - iterating from current state
 * - showing current trial
 * - taking response from user
 * - sending the response to server
 * - receiving feedback
 * - receiving updated progress
 * - iterating loop or completing page
 *
 * Constants used:
 * - TRIALS: pre-generated trials in form { iteration: trial_data, ... }
 * - TRIAL_DELAY: delay in ms after trial completed
 *
 * Page vars used:
 * - vars.progress: { total, completed, iteration, ... }
 * - vars.trial: current trial data form TRIALS
 * - vars.response: response, should be provided by ot.completeTrial({ response: ... })
 * - vars.feedback: feedback from server
 *
 * Live comminication:
 * - sending 'start'
 * - receiving 'reset' with current progress
 * - sending 'response'
 * - receiving 'feedback'
 * - receiving 'progress'
 *
 * Features:
 * - soft transition
 *   - vars.transition: "fadeout" or "fadein" css class
 *   - FADEOUT_TIME: should be time of the animation in ms
 * - measuring response time, from startTrial to completeTrial
 */

function fadeout() {
    vars.transition = "fadeout";
}

function fadein() {
    vars.transition = "fadein";
}

ot.onStartPage(function () {
    vars.progress = {};
    // inform server about page started
    // expect reply 'init'
    ot.sendLive('start');
});

ot.onLive('reset', function (data) {
    // update any progress values
    vars.progress = data.progress;
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

    ot.resetInputs();
    ot.enableInputs();
    ot.showDisplays();
    ot.startTimeMeasurement();
});

ot.onCompleteTrial(function (result) {
    // prevent extra input
    ot.disableInputs();

    // put response on page
    vars.response = result.response;

    // add iteration to keep stuff server in sync
    result.iteration = vars.progress.iteration;

    // add measured time
    result.time = ot.getTimeMeasurement();

    // send response to server
    ot.sendLive('response', result);
});

// receive feedback from server
ot.onLive('feedback', function (data) {
    // just show the feedback on page
    vars.feedback = data;
});

ot.onLive('progress', function (data) {
    // update any progress values
    Object.assign(vars.progress, data);

    // indicates that the trial is completed
    if ('completed' in data) {
        ot.completeIteration();
    }
});

ot.onCompleteIteration(function () {
    ot.delay(TRIAL_DELAY - FADEOUT_TIME, fadeout);
    ot.delay(TRIAL_DELAY, ot.nextIteration);
});

ot.onLive('failure', function (message) {
    alert(message);
    ot.completePage();
});