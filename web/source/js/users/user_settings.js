'use strict';

W.ns('W.users');

W.users.UserSettings = function () {

    return {
        get: function get(userId, settingName, successCallback, errorCallback) {
            $.ajax({
                method: 'GET',
                url: '/api/v1/users/{0}/settings'.format(userId),
                success: function (data) {
                    var setting = {};

                    if (data) {
                        $.each(data, function (index, value) {
                            if (settingName === value.setting_name) {
                                setting = value.setting_value;
                            }
                        })
                    }

                    if (successCallback) {
                        successCallback(setting);
                    }
                },
                error: function (error) {
                    console.log('Cannot get a settings for user: {1}'.format(error.responseText));

                    if (errorCallback) {
                        errorCallback(error);
                    }
                }
            });
        },

        update: function update(userId, settingName, settingValue, successCallback, errorCallback) {
            $.ajax({
                method: 'POST',
                url: '/api/v1/users/{0}/settings'.format(userId),
                dataType: 'json',
                data: JSON.stringify({
                    setting_name: settingName,
                    setting_value: settingValue
                }),
                success: function () {
                    if (successCallback) {
                        successCallback();
                    }
                },
                error: function (error) {
                    console.log('Cannot update a setting {0} for user: {1}'.format(settingName));

                    if (errorCallback) {
                        errorCallback(error);
                    }
                }
            });
        }
    };

}();
