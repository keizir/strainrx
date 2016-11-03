'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessDetail = Class.extend({

    ui: {
        $businessId: $('.business-id'),
        $btnUpdateInfo: $('.btn-update-info')
    },

    init: function init() {
        this.clickUpdateBusinessInfo();

        $('input').on('focus', function () {
            $('.error-message').text('');
        });
    },

    clickUpdateBusinessInfo: function clickUpdateBusinessInfo() {
        var that = this,
            $errorMessage = $('.error-message');

        this.ui.$btnUpdateInfo.on('click', function (e) {
            e.preventDefault();

            var businessName = $('input[name="business_name"]').val(),
                email = $('input[name="email"]').val(),
                currentEmailAddress = $('input[name="current_email"]').val();

            if (!businessName || businessName.trim().length === 0) {
                $errorMessage.text('Business Name is required');
                return;
            }

            if (!email || email.trim().length === 0) {
                $errorMessage.text('Email address is required');
                return;
            }

            if (!W.common.Constants.regex.email.test(email)) {
                $errorMessage.text('Invalid email address format');
                return;
            }

            if (email.trim() !== currentEmailAddress.trim()) {
                that.checkIfEmailRegistered(email, function (data) {
                        if (!data || data.exist) {
                            $errorMessage.text('There is already an account associated with that email address');
                            return;
                        }

                        that.updateBusinessInfo({business_name: businessName.trim(), email: email.trim()});
                    }, function () {
                        return false;
                    }
                );
            } else {
                that.updateBusinessInfo({business_name: businessName.trim(), email: currentEmailAddress.trim()});
            }
        });
    },

    checkIfEmailRegistered: function checkIfEmailRegistered(email, successCallback, errorCallback) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/users/?email={0}'.format(encodeURIComponent(email)),
            dataType: 'json',
            success: function (data) {
                successCallback(data);
            },
            error: function (error) {
                errorCallback(error);
            }
        });
    },

    updateBusinessInfo: function updateBusinessInfo(data) {
        var that = this,
            $errorMessage = $('.error-message');

        $.ajax({
            method: 'POST',
            url: '/api/v1/businesses/{0}/info'.format(that.ui.$businessId.val()),
            dataType: 'json',
            data: JSON.stringify(data),
            success: function () {
                $errorMessage.text('Business Info was updated');
                $errorMessage.removeClass('error-message');
                $errorMessage.addClass('success-message');
                setTimeout(function () {
                    $errorMessage.text('');
                    $errorMessage.addClass('error-message');
                }, 3000);
            },
            error: function (error) {
                if (error.status === 400) {
                    $errorMessage.text(JSON.parse(error.responseText).error);
                }
            }
        });
    }

});
