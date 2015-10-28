$(document).ready(function () {
	$.getJSON("/debug", function (data) {
		$("#sentiment-score").html(data.avg_score);
		$("positive").html(data.sentiment_counts.positive);
		$("negative").html(data.sentiment_counts.negative);
		$("neutral").html(data.sentiment_counts.neutral);
		$("last-updated").html(data.time);
	});
});