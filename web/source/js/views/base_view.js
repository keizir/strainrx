'use strict';

W.ns('W.views');

// using john resig's simple class inheritence see http://ejohn.org/blog/simple-javascript-inheritance/
W.views.BaseView = Class.extend({

    init: function () {
        var that = this;
        $('.resend-nav-email-link').on('click', function (e) {
            that.sendEmailVerificationEmail(e);
        });

        $('.resend-nav-b2b-email-link').on('click', function (e) {
            that.sendB2bEmailVerificationEmail(e);
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
    },

    sendB2bEmailVerificationEmail: function (e) {
        e.preventDefault();
        $.ajax({
            method: 'GET',
            url: '/api/v1/businesses/resend-email-confirmation'
        });
    }
});