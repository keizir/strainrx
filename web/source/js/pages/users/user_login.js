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
                success: function (data) {
                    console.log(data);
                },
                error: function (e, e1, e2) {
                    console.log(e);
                    console.log(e1);
                    console.log(e2);
                }
            });
        });
    }

    registerLoginButtonListener();
});