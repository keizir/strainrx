'use strict';

W.ns('W.pages');

W.pages.StrainSearchPage = Class.extend({

    init: function () {
        this.registerStep1ClickListener();
        this.registerStep1SkipClickListener();

        this.registerStep2ClickListener();
        this.registerStep2SkipClickListener();

        this.registerStep3ClickListener();
        this.registerStep3SkipClickListener();

        this.registerStep4ClickListener();
        this.registerStep4SkipClickListener();

        $('.strain-effect').on('click', function () {
            $(this).toggleClass('active');
        });
    },

    registerStep1ClickListener: function () {
        var that = this;
        $('.btn-step-1').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 1,
                sativa: $('input[name="sativa"]').is(":checked"),
                hybrid: $('input[name="hybrid"]').is(":checked"),
                indica: $('input[name="indica"]').is(":checked")
            }, '/search/strain/wizard/2/');
        });
    },

    registerStep1SkipClickListener: function () {
        var that = this;
        $('.btn-skip-1').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 1, skipped: true}, '/search/strain/wizard/2/');
        });
    },

    registerStep2ClickListener: function () {
        var that = this;
        $('.btn-step-2').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 2
            }, '/search/strain/wizard/3/');
        });
    },

    registerStep2SkipClickListener: function () {
        var that = this;
        $('.btn-skip-2').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 2, skipped: true}, '/search/strain/wizard/3/');
        });
    },

    registerStep3ClickListener: function () {
        var that = this;
        $('.btn-step-3').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 3
            }, '/search/strain/wizard/4/');
        });
    },

    registerStep3SkipClickListener: function () {
        var that = this;
        $('.btn-skip-3').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 3, skipped: true}, '/search/strain/wizard/4/');
        });
    },

    registerStep4ClickListener: function () {
        var that = this;
        $('.btn-step-4').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 4
            }, '/search/strain/results/');
        });
    },

    registerStep4SkipClickListener: function () {
        var that = this;
        $('.btn-skip-4').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 4, skipped: true}, '/search/strain/results/');
        });
    },

    sendDataToWizard: function (data, successUrl) {
        $.ajax({
            method: 'POST',
            url: '/api/v1/search/strain',
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
    }
});
