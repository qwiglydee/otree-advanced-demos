/** format number as text with + or - sign */
function format_score(score) {
    if (score == 0) return "0";
    if (score > 0) return `+${score}`;
    if (score < 0) return `${score}`;
}

/** format number as gain of point(s) */
function format_gain(score) {
    let points = Math.abs(score) == 1 ? "point" : "points";
    if (score == 0) return `got no ${points}`;
    if (score > 0) return `earned ${score} ${points}`;
    if (score < 0) return `lost ${-score} ${points}`;
}

