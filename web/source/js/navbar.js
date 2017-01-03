'use strict';

W.ns('W');

W.Navbar = function () {

    return {
        init: function init(options) {
            this.authenticated = options && options.authenticated;
            this.location = options && options.location;

            if (this.authenticated) {
                this.updateAddress();
            }

            if (AUTHENTICATED && !EMAIL_VERIFIED) {
                $('.strain-wizard-link').on('click', function (e) {
                    e.preventDefault();
                    W.common.VerifyEmailDialog();
                });
            }
        },

        updateAddress: function (location) {
            var l = location || this.location, location_parts = [];
            if (l) {
                if (l.street1) {
                    $('.nav-bar-user-street').text(l.street1);
                }

                if (l.city) {
                    location_parts.push(l.city);
                }

                if (l.state) {
                    location_parts.push(l.state);
                }

                if (l.zipcode) {
                    location_parts.push(l.zipcode);
                }

                if (location_parts.length === 0 && l.location_raw && !_.isEmpty(l.location_raw)) {
                    var parsed = JSON.parse(l.location_raw);
                    if (parsed && parsed[0] && parsed[0].formatted_address) {
                        location_parts.push(parsed[0].formatted_address);
                    }
                }

                $('.nav-bar-user-location').text(location_parts.join(', '));
            }
        }
    };
}();
