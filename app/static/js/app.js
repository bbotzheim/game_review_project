
$(document).ready( function() {

    $("button.submit").click(function(event) {
        var platform = $("select#platform").val();
        var genres = $("select#genre").val();
        var game = $("input#game").val();

        var request = {game: game, genres: genres.join(","), platform: platform};
        var results_ele = $(".app .results");
        console.log(request);
        $.getJSON("api/_recommend-games", request, function(data) {
            results_ele.empty();
            results_ele.css("display", "block");
            if (data.result === "") {
                results_ele.text(data.error);
            }
            else {
                data.result.forEach(function (item, index) {
                    // var result_ele = document.createElement("div");
                    // result_ele.text(item);
                    // results_ele.append(result_ele)

                    var res = results_ele.append("<p>", item);
                    // res.text(item);

                });
            }
        });
    });
});
