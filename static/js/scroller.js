// var elems = document.getElementsByClassName("scroller_sync");


// function foo() {
//     var top = this.scrollTop;

//     for (i = 0; i < elems.length; i++) {
//         elems[i].scrollTop=top;
//     }
// }

// for (i = 0; i < elems.length; i++) {
//     elems[i].addEventListener("scroll", foo);
// }
jQuery(function ($) {
    $(".scroller").on("scroll", function () {
        $(".scroller").scrollTop($(this).scrollTop());
    });
});