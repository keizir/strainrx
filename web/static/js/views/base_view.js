'use strict';

W.ns('W.views');

// using john resig's simple class inheritence see http://ejohn.org/blog/simple-javascript-inheritance/
W.views.BaseView = Class.extend({

    init: function () {
        var that = this;
        $('.resend-email-link').on('click', function (e) {
            that.sendEmailVerificationEmail(e);
        });
    },

    show: function () {
        this.elem.fadeIn();
    },

    hide: function () {
        this.elem.hide();
    },

    sendEmailVerificationEmail: function (e) {
        e.preventDefault();
        $.ajax({
            method: 'GET',
            url: '/api/v1/users/resend-email-confirmation'
        });
    }
});