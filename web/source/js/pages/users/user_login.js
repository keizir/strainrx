'use strict';

$(document).ready(function () {
    function registerLoginButtonListener() {
        $('.send-login').on('click', function (e) {
            e.preventDefault();

            var email = $('#login').val(),
                password = $('#password').val();

            $.ajax({
                method: 'POST',
                url: '/api/v1/users/login',
                dataType: 'json',
                data: JSON.stringify({email: email, password: password}),
                success: function () {
                    window.location.href = '/';
                },
                error: function (error) {
                    if (error.status === 400) {
                        $('.error-message').text(JSON.parse(error.responseText).error);
                    }
                }
            });
        });
    }

    registerLoginButtonListener();
});