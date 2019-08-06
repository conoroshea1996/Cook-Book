$(document).ready(function () {
    $('#drop').click(function () {
        $('#ingredients-list').slideToggle('slow');
    });
    $('#dropit').click(function () {
        $('#instuctions-list').slideToggle('slow');
    });

    $('#sign_in_like').click(function () {
        $('.warning-message').slideDown(function () {
            setTimeout(function () {
                $('.warning-message').slideUp();
            }, 3000);
        })
    })
    $('#x').delay(3000).fadeOut('slow');

});
