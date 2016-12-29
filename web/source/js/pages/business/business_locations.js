'use strict';

W.ns('W.pages.business');

W.pages.business.BusinessLocations = Class.extend({

    errors: {},

    locations: {},

    ui: {
        $businessId: $('.business-id'),
        $btnAddLocation: $('.btn-add-location'),
        $btnUpdateLocations: $('.btn-update-locations')
    },

    regions: {
        $locations: $('.locations-group')
    },

    templates: {
        $location: _.template($('#business_location').html())
    },

    init: function init() {
        var that = this;

        this.retrieveLocations(function (locations) {
            $.each(locations, function (i, location) {
                that.locations[location.id] = location;
                that.regions.$locations.append(that.templates.$location({
                    'l': location, 'buildDisplayName': that.buildLocationDisplayName
                }));
                that.prepareAndShowDeliveryDistanceSlider(location.id, location.delivery);
                that.changeAddress(location, i);
            });

            that.registerAllInputEvents($('input'));
            that.clickAddLocation();
            that.clickUpdateLocations();
            that.clickRemoveLocation($('.btn-trash'));
        });
    },

    buildLocationDisplayName: function buildLocationDisplayName(location) {
        return W.common.Format.formatAddress(location);
    },

    changeAddress: function changeAddress(location, pacContainerIndex) {
        var that = this,
            $locationInput = $('input[name="address__{0}"]'.format(location.id));

        this.GoogleLocations = new W.Common.GoogleLocations({
            $input: $locationInput.get(0),
            pacContainerIndex: pacContainerIndex
        });

        this.GoogleLocations.initGoogleAutocomplete(
            function (autocomplete, $input) {
                var $el = $($input),
                    a = that.GoogleLocations.getAddressFromAutocomplete(autocomplete),
                    id = location.id || location.tmp_id;

                if (!a || !a.street1 || !a.city || !a.state || !a.zipcode) {
                    that.addError(id, 'address__{0}'.format(id), 'Enter an address with street, city, state and zipcode.');
                } else {
                    $el.val(W.common.Format.formatAddress(a));
                    $el.blur();

                    that.locations[id].street1 = a.street1;
                    that.locations[id].city = a.city;
                    that.locations[id].state = a.state;
                    that.locations[id].zip_code = a.zipcode;
                    that.locations[id].lat = a.lat;
                    that.locations[id].lng = a.lng;
                    that.locations[id].location_raw = a.location_raw;
                }
            },
            function (results, status, $input) {
                if (status === 'OK') {
                    var a = that.GoogleLocations.getAddressFromPlace(results[0]),
                        id = location.id || location.tmp_id,
                        $el = $($input);

                    $el.val(W.common.Format.formatAddress(a));
                    $el.blur();

                    that.locations[id].street1 = a.street1;
                    that.locations[id].city = a.city;
                    that.locations[id].state = a.state;
                    that.locations[id].zip_code = a.zipcode;
                    that.locations[id].lat = a.lat;
                    that.locations[id].lng = a.lng;
                    that.locations[id].location_raw = a.location_raw;
                }
            });

        $locationInput.on('focusout', function () {
            that.updateLocation(location, $(this));
        });
    },

    retrieveLocations: function retrieveLocations(successCallback) {
        $.ajax({
            method: 'GET',
            url: '/api/v1/businesses/{0}/locations/0'.format(this.ui.$businessId.val()),
            success: function (data) {
                successCallback(data.locations);
            }
        });
    },

    registerAllInputEvents: function registerAllInputEvents($input) {
        var that = this;

        $input.on('focusout', function () {
            that.updateLocationInputFields($(this));
        });

        $input.on('change', function () {
            that.updateLocationCheckboxFields($(this));
        });
    },

    updateLocationInputFields: function updateLocationInputFields($input) {
        if ($input.prop('type') === 'text' || $input.prop('type') === 'number') {
            var that = this,
                inputValue = $input.val(),
                inputName = $input.prop('name'),
                inputNameParts = inputName.split('__'),
                fieldName = inputNameParts[0],
                locationId = inputNameParts[1],
                messageRegion = $('.error-message-{0}'.format(inputNameParts[1]));

            if (!inputValue || inputValue.trim().length === 0) {
                var $label = $('label[for="{0}"]'.format(inputName)),
                    message = '{0} is required'.format($label.text());

                that.addError(locationId, inputName, message);
                messageRegion.text(message);
                return;
            }

            messageRegion.text('');
            $('.common-error-messages').text('');

            $.each(this.locations, function (index) {
                if (index === locationId.toString()) {
                    that.cleanError(locationId, inputName);

                    if (fieldName === 'location_name') {
                        that.locations[index].location_name = inputValue;
                    }
                }
            });
        }
    },

    updateLocation: function updateLocation(location, $input) {
        var that = this,
            geoCoder = new google.maps.Geocoder();

        geoCoder.geocode({'address': '{0}'.format($input.val())},
            function (results, status) {
                if (status === 'OK') {
                    if (results && results[0]) {
                        var a = that.GoogleLocations.getAddressFromPlace(results[0]);

                        that.locations[location.id].street1 = a.street1;
                        that.locations[location.id].city = a.city;
                        that.locations[location.id].state = a.state;
                        that.locations[location.id].zip_code = a.zipcode;
                        that.locations[location.id].lat = a.lat;
                        that.locations[location.id].lng = a.lng;
                        that.locations[location.id].location_raw = a.location_raw;
                    }
                } else {
                    console.log('Geocoder failed due to: ' + status);
                }
            });
    },

    updateLocationCheckboxFields: function updateLocationCheckboxFields($input) {
        if ($input.prop('type') === 'checkbox') {
            var that = this,
                inputName = $input.prop('name'),
                inputNameParts = inputName.split('__'),
                fieldName = inputNameParts[0],
                locationId = inputNameParts[1],
                messageRegion = $('.error-message-{0}'.format(inputNameParts[1]));

            $('.common-error-messages').text('');
            messageRegion.text('');

            $.each(this.locations, function (index) {
                if (index === locationId.toString()) {
                    that.cleanError(locationId, 'delivery__{0}'.format(locationId));
                    that.cleanError(locationId, 'dispensary__{0}'.format(locationId));

                    if (fieldName === 'dispensary') {
                        that.locations[index].dispensary = $input.is(':checked');
                    }

                    if (fieldName === 'delivery') {
                        that.locations[index].delivery = $input.is(':checked');
                        that.prepareAndShowDeliveryDistanceSlider(locationId, that.locations[index].delivery);
                    }

                    if (!that.locations[index].dispensary && !that.locations[index].delivery) {
                        messageRegion.text('Business type is required');
                        that.addError(locationId, inputName, 'Business type is required');
                    }
                }
            });
        }
    },

    prepareAndShowDeliveryDistanceSlider: function prepareAndShowDeliveryDistanceSlider(locationId, isDelivery) {
        var $sliderArea = $('.slider-area-{0}'.format(locationId));
        if (isDelivery) {
            $sliderArea.removeClass('hidden');
            this.showDeliveryDistanceSlider($sliderArea, locationId);
        } else {
            $sliderArea.addClass('hidden');
        }
    },

    showDeliveryDistanceSlider: function showDeliveryDistanceSlider($sliderArea, locationId) {
        var that = this,
            $sliderValue = $sliderArea.find('.slider-value'),
            $slider = $sliderArea.find('.slider-{0}'.format(locationId));
        $slider.slider({
            range: 'min',
            value: that.locations[locationId].delivery_radius ? that.locations[locationId].delivery_radius : 5,
            min: 5, max: 50, step: 0.5,
            slide: function (event, ui) {
                $sliderValue.text('{0} Miles'.format(ui.value));
                that.locations[locationId].delivery_radius = ui.value;
            }
        });
        $sliderValue.text('{0} Miles'.format($slider.slider('value')));
    },

    clickAddLocation: function clickAddLocation() {
        var that = this;

        this.ui.$btnAddLocation.on('click', function (e) {
            e.preventDefault();

            var locationClientId = 'tmpId{0}'.format(new Date().getTime());
            that.locations[locationClientId] = {
                tmp_id: locationClientId,
                location_name: null, manager_name: null, location_email: null,
                phone: null, ext: null,
                dispensary: false, delivery: false, delivery_radius: null,
                mon_open: null, mon_close: null,
                tue_open: null, tue_close: null,
                wed_open: null, wed_close: null,
                thu_open: null, thu_close: null,
                fri_open: null, fri_close: null,
                sat_open: null, sat_close: null,
                sun_open: null, sun_close: null
            };
            that.regions.$locations.append(that.templates.$location({
                'l': {'id': locationClientId}, 'buildDisplayName': that.buildLocationDisplayName
            }));
            that.registerAllInputEvents($('.location-{0}'.format(locationClientId)).find('input'));
            that.changeAddress({'id': locationClientId}, $('.pac-container').length);
            that.clickRemoveLocation($('.btn-trash-{0}'.format(locationClientId)));
            that.addError(locationClientId, 'delivery__{0}'.format(locationClientId), 'Business type is required');
        });
    },

    clickUpdateLocations: function clickUpdateLocations() {
        var that = this;

        this.ui.$btnUpdateLocations.on('click', function (e) {
            e.preventDefault();

            $.each($('input[type="text"], input[type="number"]'), function (i, $input) {
                var v = $input.value;
                if (!v || v.trim().length === 0) {
                    var inputName = $input.name,
                        $label = $('label[for="{0}"]'.format(inputName)),
                        inputNameParts = inputName.split('__'),
                        locationId = inputNameParts[1],
                        message = '{0} is required'.format($label.text());

                    that.addError(locationId, inputName, message);
                }
            });

            $.each(that.locations, function (i, l) {
                if (!l.street1 || !l.city || !l.state || !l.zip_code) {
                    that.addError(l.id || l.tmp_id, 'address__{0}'.format(l.id || l.tmp_id), 'Enter an address with street, city, state and zipcode.');
                }
            });

            if (that.hasErrors()) {
                $.each(that.errors, function (locationId, locationErrors) {
                    var locationError = '';

                    $.each(locationErrors, function (index, error) {
                        locationError += '<p>' + error.message + '</p>';
                    });

                    $('.error-message-{0}'.format(locationId)).html(locationError);
                    $('.common-error-messages').text('Some locations have errors');
                });
                return;
            }

            var locationsToSend = [];
            $.each(that.locations, function (locationId, location) {
                delete location.tmp_id;
                locationsToSend.push(location);
            });

            $.ajax({
                method: 'PUT',
                url: '/api/v1/businesses/{0}/locations/0'.format(that.ui.$businessId.val()),
                dataType: 'json',
                data: JSON.stringify({'locations': locationsToSend}),
                success: function () {
                    that.showSuccessMessage('Locations were updated');
                    window.location.reload();
                },
                error: function (error) {
                    if (error.status === 400) {
                        var errorJson = W.common.Parser.parseJson(error.responseText);
                        $('.common-error-messages').text(errorJson.error);
                    }
                }
            });
        });
    },

    clickRemoveLocation: function clickRemoveLocation($btnTrash) {
        var that = this;

        $btnTrash.on('click', function () {
            var locationId = $(this).prop('id');
            if (locationId.startsWith('tmpId')) {
                delete that.locations[locationId];
                delete that.errors[locationId];
                $('.location-{0}'.format(locationId)).html('');
                return;
            }

            var $removeLocationDialog = $('.remove-location-dialog');

            $removeLocationDialog.find('.btn-remove').on('click', function () {
                $removeLocationDialog.dialog('close');
                $.ajax({
                    method: 'DELETE',
                    url: '/api/v1/businesses/{0}/locations/{1}'.format(that.ui.$businessId.val(), locationId),
                    success: function () {
                        that.showSuccessMessage('Location was removed');
                        window.location.reload();
                    }
                });
            });

            $removeLocationDialog.find('.btn-cancel').on('click', function () {
                $removeLocationDialog.dialog('close');
            });

            W.common.ConfirmDialog($removeLocationDialog);
        });
    },

    showSuccessMessage: function showSuccessMessage(message) {
        var $commonError = $('.common-error-messages');
        $commonError.text(message);
        $commonError.removeClass('error-message').addClass('success-message');
        setTimeout(function () {
            $commonError.text('');
            $commonError.addClass('error-message').removeClass('success-message');
        }, 2000);
    },

    hasErrors: function hasErrors() {
        return !_.isEmpty(this.errors);
    },

    addError: function addError(locationId, inputName, message) {
        if (!this.errors[locationId]) {
            this.errors[locationId] = [];
        }

        if (this.errors[locationId].length === 0) {
            this.errors[locationId].push({field: inputName, message: message});
        } else {
            var filtered = _.filter(this.errors[locationId], function (e) {
                return e.field === inputName;
            });

            if (filtered.length === 0) {
                this.errors[locationId].push({field: inputName, message: message});
            }
        }
    },

    cleanError: function cleanError(locationId, inputName) {
        if (this.errors[locationId]) {
            for (var i = 0; i < this.errors[locationId].length; i++) {
                if (this.errors[locationId][i].field === inputName) {
                    this.errors[locationId].splice(i, 1);
                    break;
                }
            }

            if (this.errors[locationId].length === 0) {
                delete this.errors[locationId];
            }
        }
    }

});
