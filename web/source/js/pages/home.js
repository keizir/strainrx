'use strict';

W.ns('W.pages');

W.pages.HomePage = Class.extend({

    init: function init(options) {
        this.location = options && options.location;
        this.authenticated = options && options.authenticated;
        this.userId = options && options.userId;

        this.initStrainLookupField();
        this.clickLookupSubmit();
        this.changeLocation();
        this.preFillUserLocation();
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
        if (this.location) {
            $('.your-location-value').val(W.common.Format.formatAddress(this.location)).trigger('change');
        }
    },

    changeLocation: function changeLocation() {
        var that = this,
            GoogleLocations = new W.Common.GoogleLocations({$input: $('#location').get(0)});

        GoogleLocations.initGoogleAutocomplete(
            function (autocomplete, $input) {
                var $el = $($input),
                    address = GoogleLocations.getAddressFromAutocomplete(autocomplete);

                $el.val(W.common.Format.formatAddress(address));
                $el.blur();

                that.saveUserLocation(address);
            },
            function (results, status, $input) {
                if (status === 'OK') {
                    var $el = $($input),
                        address = GoogleLocations.getAddressFromPlace(results[0]);

                    $el.val(W.common.Format.formatAddress(address));
                    $el.blur();

                    that.saveUserLocation(address);
                }
            },
            function ($input) {
                var $removeBtn = $('.remove-location');
                $('.check').hide();
                $removeBtn.removeClass('hidden');
                $removeBtn.on('click', function () {
                    if (that.authenticated) {
                        // TODO remove when auth
                    } else {
                        Cookies.remove('user_geo_location');
                    }

                    $removeBtn.addClass('hidden');
                    $('.check').show();
                    $($input).val('');
                });
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
