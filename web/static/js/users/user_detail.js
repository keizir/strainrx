'use strict';

W.ns('W.users');

W.users.DetailPage = Class.extend({

    init: function () {
        this.registerUpdateUserInfoClickListener();
    },

    registerUpdateUserInfoClickListener: function () {
        $('.btn-update-user-info').on('click', function (e) {
            e.preventDefault();

            $.ajax({
                method: 'PUT',
                url: '/api/v1/users/' + $('input[name="uid"]').val() + '/',
                dataType: 'json',
                data: JSON.stringify(collectUserData()),
                success: function () {
                    handleSuccess();
                },
                error: function (error) {
                    handleError(error);
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
                    'gender': gender !== defaultSelectValue ? gender : null,
                    'pwd': $('input[name="pwd"]').val(),
                    'pwd2': $('input[name="pwd2"]').val()
                };
            }

            function handleSuccess() {
                var $messages = $('.messages');
                $messages.text('You profile information has been successfully updated');
                $messages.removeClass('error-message');
                $messages.addClass('success-message');

                setTimeout(function () {
                    $messages.text('');
                }, 3000);
            }

            function handleError(error) {
                if (error.status === 400) {
                    var $messages = $('.messages');

                    var errorText = JSON.parse(error.responseText);
                    $messages.text(errorText.error ?
                        errorText.error : errorText.zipcode ?
                        'Zip Code may contain max 10 characters' : errorText.email ?
                        'Email format is invalid' : 'Exception');

                    $messages.removeClass('success-message');
                    $messages.addClass('error-message');
                }
            }
        });
    }
});
