'use strict';

W.ns('W.views');

// using john resig's simple class inheritence see http://ejohn.org/blog/simple-javascript-inheritance/
W.views.BaseView = Class.extend({

    init: function (cfg) {
        var cfg = cfg || {},
            that = this;

        this.name = (cfg.name === undefined) ? console.error('name is undefined') : cfg.name;
        this.elem = (cfg.elem === undefined) ? console.error('elem is undefined') : $(cfg.elem);

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