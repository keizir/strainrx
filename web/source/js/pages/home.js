'use strict';

W.ns('W.pages');

W.pages.HomePage = Class.extend({

    init: function init(options) {
        this.location = options && options.location;
        this.authenticated = options && options.authenticated;
        this.userId = options && options.userId;

        this.initStrainLookupField();
        this.clickLookupSubmit();
        this.preFillUserLocation();
        this.changeLocation();
    },

    initStrainLookupField: function initStrainLookupField() {
        var lookupTemplate = _.template($('#strain-lookup-field').html());
        $('.strain-name-field').html(lookupTemplate({
            'lookup_placeholder': 'Example: Blue Dream, Maiu Wowie, Pineapple express'
        }));
        new W.pages.strain.StrainLookup();
    },

    clickLookupSubmit: function clickLookupSubmit() {
        $('.lookup-submit').on('click', function (e) {
            e.preventDefault();
            var $input = $('.lookup-input'),
                strainName = $input.val(),
                strainSlug = $input.attr('payload-slug');

            if (strainName && strainSlug) {
                window.location.href = '/search/strain/{0}'.format(strainSlug);
            }
        });
    },

    preFillUserLocation: function preFillUserLocation() {
        var l = this.location, location = [];
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

            $('.your-location-value').val(location.join(', '));
        }
    },

    changeLocation: function changeLocation() {
        var that = this,
            GoogleLocations = new W.Common.GoogleLocations({$input: $('#location').get(0)});

        GoogleLocations.initGoogleAutocomplete(
            function (autocomplete) {
                var address = GoogleLocations.getAddressFromAutocomplete(autocomplete);
                that.saveUserLocation(address);
            },
            function (results, status) {
                if (status === 'OK') {
                    var address = GoogleLocations.getAddressFromPlace(results[0]);
                    that.saveUserLocation(address);
                }
            });
    },

    saveUserLocation: function saveUserLocation(data) {
        if (data) {
            var that = this;
            if (this.authenticated) {
                $.ajax({
                    method: 'POST',
                    url: '/api/v1/users/{0}/geo_locations'.format(that.userId),
                    data: JSON.stringify(data)
                });
            } else {
                delete data.location_raw;
                Cookies.set('user_geo_location', JSON.stringify(data));
            }
        }
    }
});
