'use strict';

W.ns('W.pages.b2c');

W.pages.b2c.AlmostDone = function () {

    return {
        init: function () {
            $('.resend-email-link').on('click', function (e) {
                e.preventDefault();
                $.ajax({
                    method: 'GET',
                    url: '/api/v1/users/resend-email-confirmation'
                });
            });
        }
    };
}();
