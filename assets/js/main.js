////////////////
// Footer
////////////////
function updateFooter() {
    var footerH = $("#footer").height();
    var contentH = $("#header").height() + $("#page-content").height();
    var windowH = $(window).height();

    if (contentH + footerH > windowH) {
        $("#footer").removeClass("fixed");
    } else {
        $("#footer").addClass("fixed");
    }
}


$(document).ready(function () {
    $(window).resize(function () {
        updateFooter();
    });

    updateFooter();
    setTimeout(function () { updateFooter(); }, 150)
    setTimeout(function () { updateFooter(); }, 500)
    setTimeout(function () { updateFooter(); }, 1000)
    //startTutorial()
});
