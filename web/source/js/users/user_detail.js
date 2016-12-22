'use strict';

W.ns('W.users');

W.users.DetailPage = Class.extend({

    ui: {
        $messagesRegion: $('.messages')
    },

    init: function () {
        var that = this;

        $('select').focus(function () {
            that.ui.$messagesRegion.text('');
        });

        this.preFillUserAddress();
        this.changeAddress();

        this.clickUpdateUserInfo();
        this.clickChangePassword();
    },

    preFillUserAddress: function () {
        var that = this;
        $.ajax({
            method: 'GET',
            url: '/api/v1/users/{0}/geo_locations'.format($('input[name="uid"]').val()),
            success: function (data) {
                if (data && data.location) {
                    var l = data.location, location = [];
                    that.location = data.location;

                    if (l) {
                        if (l.street1) {
                            location.push(l.street1);
                        }

                        if (l.city) {
                            location.push(l.city);
                        }

                        if (l.state) {
                            location.push(l.state);
                        }

                        if (l.zipcode) {
                            location.push(l.zipcode);
                        }

                        if (location.length === 0 && l.location_raw) {
                            var parsed = JSON.parse(l.location_raw);
                            if (parsed && parsed[0] && parsed[0].formatted_address) {
                                location.push(parsed[0].formatted_address);
                            }
                        }

                        $('input[name="address"]').val(location.join(', '));
                    }
                }
            }
        });
    },

    changeAddress: function changeAddress() {
        var that = this,
            GoogleLocations = W.Common.GoogleLocations;

        GoogleLocations.initGoogleAutocomplete($('input[name="address"]').get(0), function (autocomplete) {
            that.location = GoogleLocations.getAddressFromAutocomplete(autocomplete);
        });
    },

    clickUpdateUserInfo: function clickUpdateUserInfo() {
        var that = this;
        $('.btn-update-user-info').on('click', function (e) {
            e.preventDefault();

            var data = collectUserData();
            if (isValid(data)) {
                updateTimezone(data, function () {
                    $.ajax({
                        method: 'PUT',
                        url: '/api/v1/users/' + $('input[name="uid"]').val() + '/',
                        dataType: 'json',
                        data: JSON.stringify(data),
                        success: function () {
                            that.showSuccessMessage('You profile information has been successfully updated');
                            W.Navbar.updateAddress(data.location);
                        },
                        error: function (error) {
                            that.showErrorMessage(error);
                        }
                    });
                });
            }

            function collectUserData() {
                var defaultSelectValue = '- Select One -',
                    birthMonth = $('select[name="birth_month"]').val(),
                    birthDay = $('select[name="birth_day"]').val(),
                    birthYear = $('select[name="birth_year"]').val(),
                    gender = $('select[name="gender"]').val(),
                    timezone = $('select[name="timezone"]').val();

                return {
                    'first_name': $('input[name="first_name"]').val(),
                    'last_name': $('input[name="last_name"]').val(),
                    'email': $('input[name="email"]').val(),
                    'birth_month': birthMonth !== defaultSelectValue ? birthMonth : null,
                    'birth_day': birthDay !== defaultSelectValue ? birthDay : null,
                    'birth_year': birthYear !== defaultSelectValue ? birthYear : null,
                    'gender': gender !== defaultSelectValue ? gender : null,
                    'timezone': timezone !== defaultSelectValue ? timezone : null,
                    'location': that.location
                };
            }

            function isValid(data) {
                var birthDay = data.birth_day,
                    birthMonth = data.birth_month;

                if (birthDay && birthMonth && birthDay > 28 && birthMonth === 'feb') {
                    that.displayErrorMessage('February has only 28 days');
                    return false;
                }

                return true;
            }

            function updateTimezone(data, callback) {
                if (data.timezone === null) {
                    var xsr = new XMLHttpRequest();
                    xsr.open("GET", 'https://maps.googleapis.com/maps/api/timezone/json?location={0},{1}&timestamp={2}&key={3}'
                        .format(data.location.lat, data.location.lng, '1458000000', GOOGLE_API_KEY));
                    xsr.onload = function () {
                        var d = JSON.parse(xsr.responseText);
                        data.timezone = d.timeZoneId;
                        callback();
                    };
                    xsr.send();
                } else {
                    callback();
                }
            }
        });
    },

    clickChangePassword: function clickChangePassword() {
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

    showSuccessMessage: function showSuccessMessage(message) {
        var $messagesRegion = this.ui.$messagesRegion;
        $messagesRegion.text(message);
        $messagesRegion.removeClass('error-message');
        $messagesRegion.addClass('success-message');
        setTimeout(function () {
            $messagesRegion.text('');
        }, 3000);
    },

    showErrorMessage: function showErrorMessage(error) {
        var that = this;
        if (error.status === 400) {
            var errorText = JSON.parse(error.responseText);
            that.displayErrorMessage(errorText.error ?
                errorText.error : errorText.zipcode ?
                'Zip Code may contain max 10 characters' : errorText.email ?
                'Email format is invalid' : 'Exception');
        }
    },

    displayErrorMessage: function displayErrorMessage(message) {
        var $messagesRegion = this.ui.$messagesRegion;
        $messagesRegion.text(message);
        $messagesRegion.removeClass('success-message');
        $messagesRegion.addClass('error-message');
    }
});
