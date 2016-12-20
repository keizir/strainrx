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

        this.clickUpdateUserInfo();
        this.clickChangePassword();
    },

    clickUpdateUserInfo: function clickUpdateUserInfo() {
        var that = this;
        $('.btn-update-user-info').on('click', function (e) {
            e.preventDefault();

            var data = collectUserData();
            if (isValid(data)) {
                updateLocationData(data, function () {
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
                    'location': {
                        'street1': '',
                        'city': $('input[name="city"]').val() || '',
                        'state': $('input[name="state"]').val() || '',
                        'zipcode': $('input[name="zipcode"]').val() || ''
                    }
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

            function updateLocationData(data, callback) {
                var l = data.location;
                if (l.city || l.state || l.zipcode) {
                    var geoCoder = new google.maps.Geocoder();
                    geoCoder.geocode({'address': '{0}, {1}, {2}'.format(l.zipcode, l.city, l.state)},
                        function (results, status) {
                            if (status === 'OK') {
                                if (results && results[0].geometry) {
                                    data.location.lat = results[0].geometry.location.lat();
                                    data.location.lng = results[0].geometry.location.lng();
                                    data.location.location_raw = JSON.stringify(results);

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
                                } else {
                                    callback();
                                }
                            } else if (status === 'ZERO_RESULTS') {
                                alert('Invalid location');
                            } else {
                                console.log('Geocoder failed due to: ' + status);
                            }
                        });
                } else {
                    data.location.lat = null;
                    data.location.lng = null;
                    data.location.location_raw = JSON.stringify({});
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
