'use strict';

W.ns('W.pages');

W.pages.B2CSignUpPage = Class.extend({

    init: function (cfg) {
        var config = cfg || {};

        this.name = (config.name === undefined) ? console.error('name is undefined') : config.name;
        this.elem = (config.elem === undefined) ? console.error('elem is undefined') : $(config.elem);

        this.registerStep1ClickListener();
        this.registerStep2ClickListener();
        this.registerStep3ClickListener();
        this.registerStep4ClickListener();
        this.registerStep5ClickListener();

        this.registerResendEmailLinkClickListener();
    },

    registerStep1ClickListener: function () {
        var that = this;
        $('.btn-step-1').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 1,
                firstName: $('input[name="firstName"]').val(),
                lastName: $('input[name="lastName"]').val(),
                token: $('input[name="token"]').val()
            }, '/users/signup/wizard/2/');
        });
    },

    registerStep2ClickListener: function () {
        var that = this;
        $('.btn-step-2').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 2,
                age: $('input[name="age"]').is(":checked"),
                token: $('input[name="token"]').val()
            }, '/users/signup/wizard/3/');
        });
    },

    registerStep3ClickListener: function () {
        var that = this;
        $('.btn-step-3').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 3,
                email: $('input[name="email"]').val(),
                token: $('input[name="token"]').val()
            }, '/users/signup/wizard/4/');
        });
    },

    registerStep4ClickListener: function () {
        var that = this;
        $('.btn-step-4').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 4,
                pwd: $('input[name="pwd"]').val(),
                pwd2: $('input[name="pwd2"]').val(),
                token: $('input[name="token"]').val()
            }, '/users/signup/wizard/5/');
        });
    },

    registerStep5ClickListener: function () {
        var that = this;
        $('.btn-step-5').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 5,
                agreed: $('input[name="terms"]').is(':checked'),
                token: $('input[name="token"]').val()
            }, '/users/signup/wizard/6/');
        });
    },

    sendDataToWizard: function (data, successUrl) {
        $.ajax({
            method: 'POST',
            url: '/api/v1/users/signup',
            dataType: 'json',
            data: JSON.stringify(data),
            success: function () {
                window.location.href = successUrl;
            },
            error: function (error) {
                if (error.status === 400) {
                    $('.error-message').text(JSON.parse(error.responseText).error);
                }
            }
        });
    },

    registerResendEmailLinkClickListener: function () {
        $('.resend-email-link').on('click', function (e) {
            e.preventDefault();
            $.ajax({
                method: 'GET',
                url: '/api/v1/users/resend-email-confirmation'
            });
        });
    }
});
