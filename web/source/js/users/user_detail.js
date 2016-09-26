'use strict';

W.ns('W.users');

W.users.DetailPage = Class.extend({

    init: function () {
        this.registerUpdateUserInfoClickListener();
        this.registerChangePasswordClickListener();
    },

    registerUpdateUserInfoClickListener: function () {
        var that = this;

        $('.btn-update-user-info').on('click', function (e) {
            e.preventDefault();

            $.ajax({
                method: 'PUT',
                url: '/api/v1/users/' + $('input[name="uid"]').val() + '/',
                dataType: 'json',
                data: JSON.stringify(collectUserData()),
                success: function () {
                    that.showSuccessMessage('You profile information has been successfully updated');
                },
                error: function (error) {
                    that.showErrorMessage(error);
                }
            });

            function collectUserData() {
                var defaultSelectValue = '- Select One -',
                    birthMonth = $('select[name="birth_month"]').val(),
                    birthDay = $('select[name="birth_day"]').val(),
                    birthYear = $('select[name="birth_year"]').val(),
                    gender = $('select[name="gender"]').val();

                return {
                    'first_name': $('input[name="first_name"]').val(),
                    'last_name': $('input[name="last_name"]').val(),
                    'email': $('input[name="email"]').val(),
                    'city': $('input[name="city"]').val(),
                    'state': $('input[name="state"]').val(),
                    'zipcode': $('input[name="zipcode"]').val(),
                    'birth_month': birthMonth !== defaultSelectValue ? birthMonth : null,
                    'birth_day': birthDay !== defaultSelectValue ? birthDay : null,
                    'birth_year': birthYear !== defaultSelectValue ? birthYear : null,
                    'gender': gender !== defaultSelectValue ? gender : null
                };
            }
        });
    },

    registerChangePasswordClickListener: function () {
        var that = this;

        $('.btn-update-pwd').on('click', function (e) {
            e.preventDefault();

            var data = {
                'curPwd': $('input[name="cur_pwd"]').val(),
                'pwd': $('input[name="pwd"]').val(),
                'pwd2': $('input[name="pwd2"]').val()
            };

            $.ajax({
                method: 'POST',
                url: '/api/v1/users/' + $('input[name="uid"]').val() + '/change-pwd',
                dataType: 'json',
                data: JSON.stringify(data),
                success: function () {
                    that.showSuccessMessage('Your password has been changed')
                },
                error: function (error) {
                    that.showErrorMessage(error);
                }
            });
        });
    },

    showSuccessMessage: function (message) {
        var $messages = $('.messages');
        $messages.text(message);
        $messages.removeClass('error-message');
        $messages.addClass('success-message');
        setTimeout(function () {
            $messages.text('');
        }, 3000);
    },

    showErrorMessage: function (error) {
        if (error.status === 400) {
            var $messages = $('.messages'),
                errorText = JSON.parse(error.responseText);

            $messages.text(errorText.error ?
                errorText.error : errorText.zipcode ?
                'Zip Code may contain max 10 characters' : errorText.email ?
                'Email format is invalid' : 'Exception');

            $messages.removeClass('success-message');
            $messages.addClass('error-message');
        }
    }
});