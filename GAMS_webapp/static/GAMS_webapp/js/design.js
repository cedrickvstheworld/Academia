// Hide #MagicMenu on on scroll down
var didScroll;
var lastScrollTop = 0;
var delta = 5;
var navbarHeight = $('#MagicMenu').outerHeight();

$(window).scroll(function(event){
    didScroll = true;
});

setInterval(function() {
    if (didScroll) {
        hasScrolled();
        didScroll = false;
    }
}, 250);

function hasScrolled() {
    var st = $(this).scrollTop();

    // Make sure they scroll more than delta
    if(Math.abs(lastScrollTop - st) <= delta)
        return;

    // If they scrolled down and are past the navbar, add class .MagicMenu-up.
    // This is necessary so you never see what is "behind" the navbar.
    if (st > lastScrollTop && st > navbarHeight){
        // Scroll Down
        $('#MagicMenu').fadeOut(500);
    } else {
        // Scroll Up
        if(st + $(window).height() < $(document).height()) {
            $('#MagicMenu').fadeIn(500);
        }
    }

    lastScrollTop = st;
}


// $(document).ready( function () {
//
//     var words = [
//         ' complete data control',
//         ' access data anywhere'
//     ], i = 0;
//
//      setInterval(function () {
//          $("#secondarytext").fadeOut(function () {
//              $(this).html(words[i = (i+1)%words.length]).fadeIn();
//          });
//      },3000);
// })();


$(document).on('keypress', '.letters', function (event) {
    var regex = new RegExp("^[a-zA-Z ]+$");
    var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
    if (!regex.test(key)) {
        event.preventDefault();
        return false;
    }
});

$(document).on('keypress', '.integers', function (event) {
    var regex = new RegExp("^[0-9]+$");
    var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
    if (!regex.test(key)) {
        event.preventDefault();
        return false;
    }
});

$(document).on('keypress', '.numdash', function (event) {
    var regex = new RegExp("^[0-9-]+$");
    var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
    if (!regex.test(key)) {
        event.preventDefault();
        return false;
    }
});



$(document).ready(function(){
    setTimeout(function () {
        $("#cookieConsent").fadeIn(200);
     }, 2000);
    $("#closeCookieConsent, .cookieConsentOK").click(function() {
        $("#cookieConsent").fadeOut(200);
    });
});

