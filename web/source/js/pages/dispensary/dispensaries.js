'use strict';

W.ns('W.pages.dispensary');

W.pages.dispensary.Dispensaries = Class.extend({
    init: function init(options) {
        this.location = options && options.location;
        this.authenticated = options && options.authenticated;
        this.userId = options && options.userId;
        this.defaultImageUrl = options && options.defaultImageUrl;
        this.dispTimezone = null;
        this.dispLocation = null;
        this.browserInfo = W.detectBrowser();

        this.initDispensaryLookupField();
        this.initDispLocation();
        this.initEventHandlers();
        this.ieHack();
    },
    ieHack: function idHack() {
        if (this.browserInfo.type === W.C.IE && this.browserInfo.version <= 11) {
            $('.lookup-submit').css({
                position: 'relative',
                top: '1em'
            });
        }
    },
    initDispensaryLookupField: function initDispensaryLookupField() {
        new W.pages.dispensary.DispensaryLookup();
    },
    initEventHandlers: function initEventHandlers() {
        var that = this;

        $('.lookup-submit').on('click', function (e) {
            e.preventDefault();
            that.navigateToDispDetailPage();
        });

        $(document).on('keyup', function (e) {
            if (e.keyCode === 13) { // Enter Key
                that.navigateToDispDetailPage();
            }
        });



        $('.disp-location-label').on('click', function (e) {
            e.preventDefault();

            $('.disp-location-value').val('loading location...');
            that.clearDispLocation();

            navigator.geolocation.getCurrentPosition(function (position) {
                var geoCoder = new google.maps.Geocoder(),
                    pos = {lat: position.coords.latitude, lng: position.coords.longitude};

                geoCoder.geocode({'location': pos}, function (results, status) {
                    if (status === 'OK') {
                        if (results) {
                            that.updateDispLocationTime(that.GoogleLocations, {
                                lat: position.coords.latitude,
                                lng: position.coords.longitude
                            });
                            $('.disp-location-value').val(results[0].formatted_address);
                        }
                    } else {
                        console.log('Geocoder failed due to: ' + status);
                        $('.disp-location-value').val('');
                    }
                });
            }, function () {
                console.log('Cannot locate user');
                $('.disp-location-value').val('');
            });
        });
    },
    initDispLocation: function initDispLocation() {
        // for dispensary lookup location
        var that = this;
        this.GoogleLocations = new W.Common.GoogleLocations({$input: $('#disp-location').get(0)});

        this.GoogleLocations.initGoogleAutocomplete(
            function (autocomplete, $input) {
                var $el = $($input),
                    address = that.GoogleLocations.getAddressFromAutocomplete(autocomplete);

                that.onAddressChange($el, address);
            },
            function (results, status, $input) {
                if (status === 'OK') {
                    var $el = $($input),
                        address = that.GoogleLocations.getAddressFromPlace(results[0]);

                    that.onAddressChange($el, address);
                }
            },
            function ($input) {
                that.clearDispLocation();
            });
    },
    clearDispLocation: function clearDispLocation() {
        this.dispLocation = null;
        this.dispTimezone = null;
    },
    navigateToDispDetailPage: function navigateToDispDetailPage() {
        var $input = $('.lookup-input'),
            dispUrl = $input.attr('payload-url'),
            business_id = $input.attr('business_id');

        W.track({
            event: "DISP_LOOKUP",
            entity_id: business_id
        });

        if (dispUrl) {
            setTimeout(function(){
                window.location.href = dispUrl;
            }, 1000)
        }
    },
    updateDispLocationTime: function updateDispLocationTime(GoogleLocations, address) {
        var that = this;

        this.dispLocation = {
            lat: address.lat,
            lon: address.lng
        };

        GoogleLocations.getTimezone(address.lat, address.lng, function (json) {
            that.dispTimezone = json.timeZoneId;
        });
    },
    updateTimezone: function updateTimezone(GoogleLocations, address, success) {
        var that = this;
        GoogleLocations.getTimezone(address.lat, address.lng, function (json) {
            that.timezone = json.timeZoneId;
            success();
        });
    },
    saveUserLocation: function saveUserLocation(data) {
        if (data) {
            var that = this;
            if (this.authenticated) {
                $.ajax({
                    method: 'POST',
                    url: '/api/v1/users/{0}/geo_locations'.format(that.userId),
                    data: JSON.stringify({address: data, timezone: this.timezone})
                });
            } else {
                delete data.location_raw;
                Cookies.set('user_geo_location', JSON.stringify(data));
            }
        }
    },
    getDispLocationTime: function getDispLocationTime() {
        return {
            location: this.dispLocation,
            timezone: this.dispTimezone
        };
    },
    onAddressChange: function onAddressChange($el, address) {
        var that = this;
        $el.val(W.common.Format.formatAddress(address));
        $el.blur();

        this.updateDispLocationTime(that.GoogleLocations, address);
        this.fetchFeatured(address).success(function(data) {
            that.renderFeatured(data.locations);
        });
    },
    fetchFeatured: function fetchFeatured(address) {
        var url = '/api/v1/businesses/locations/featured/?loc=';
        var loc = {
            lat: address.lat,
            lon: address.lng
        };

        if (address.zipcode) {
            loc.zip = address.zipcode;
        }

        url = url + encodeURIComponent(JSON.stringify(loc));

        return $.ajax({
            method: 'GET',
            url: url
        });
    },
    renderFeatured: function renderFeatured(locations) {
        var defaultImageUrl = this.defaultImageUrl;
        var templateFn = _.template($('#featured-locations-template').html());
        var html = '';

        locations.forEach(function(location) {
            html += templateFn({
                url: location.url,
                location_name: location.location_name  || 'None',
                image_url: location.image_url || 'None',
                default_image_url: defaultImageUrl || 'None',
                street1: location.street1 || 'None',
                city: location.city || 'None',
                state: location.state || 'None',
                zip_code: location.zip_code || 'None',
                phone: location.phone || 'None',
                location_email: location.location_email || 'None'
            });
        });

        $('.featured-list').html(html);
    }

});